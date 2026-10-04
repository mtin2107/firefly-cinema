"""Baseline truyền thống (TF-IDF + NB/LR/SVM) cho 3 bài toán trên UIT-ViSFD.
Chọn siêu tham số trên Dev, báo cáo trên Test. Có ablation: văn bản thô vs đã chuẩn hóa."""
import sys, json, time
import numpy as np, pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix
sys.path.insert(0, "src")
from common import ASPECTS, POLARITIES

P = "processed"
tr, dv, te = (pd.read_csv(f"{P}/{s}.csv") for s in ["train", "dev", "test"])
tr_p, dv_p, te_p = (pd.read_csv(f"{P}/{s}_aspect_sentiment.csv") for s in ["train", "dev", "test"])
RES = {}


def feats(col, a, b, c):
    w = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    ch = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=150000)
    Xa = hstack([w.fit_transform(a[col].fillna("")), ch.fit_transform(a[col].fillna(""))]).tocsr()
    tf = lambda d: hstack([w.transform(d[col].fillna("")), ch.transform(d[col].fillna(""))]).tocsr()
    return Xa, tf(b), tf(c)


def models(task):
    return {
        "ComplementNB": [ComplementNB(alpha=a) for a in (0.1, 0.3, 1.0)],
        "LogReg": [LogisticRegression(C=c, max_iter=2000, class_weight="balanced") for c in (1, 5, 20)],
        "LinearSVC": [LinearSVC(C=c, class_weight="balanced") for c in (0.1, 0.3, 1.0)],
    }


def best_by_dev(cands, Xtr, ytr, Xdv, ydv, metric):
    best, bs = None, -1
    for m in cands:
        m.fit(Xtr, ytr)
        s = metric(ydv, m.predict(Xdv))
        if s > bs:
            best, bs = m, s
    return best, bs


# ---------- Task A: bình luận có chứa ý kiến tiêu cực? (nhị phân) ----------
print("== Task A: has_negative ==")
RES["A_has_negative"] = {}
for col in ["text_raw", "text_norm"]:
    Xtr, Xdv, Xte = feats(col, tr, dv, te)
    for name, cands in models("A").items():
        m, ds = best_by_dev(cands, Xtr, tr.has_negative, Xdv, dv.has_negative, lambda y, p: f1_score(y, p, average="macro"))
        pred = m.predict(Xte)
        r = {"dev_macroF1": round(ds, 4), "test_macroF1": round(f1_score(te.has_negative, pred, average="macro"), 4),
             "test_F1_negative": round(f1_score(te.has_negative, pred), 4),
             "test_acc": round(accuracy_score(te.has_negative, pred), 4), "params": str(m)}
        RES["A_has_negative"][f"{name}|{col}"] = r
        print(name, col, r["test_macroF1"], r["test_F1_negative"])

# ---------- Task B: phát hiện khía cạnh (đa nhãn) ----------
print("== Task B: aspect detection ==")
RES["B_aspect_detection"] = {}
Ytr = tr[[f"asp_{a}" for a in ASPECTS]].values; Ydv = dv[[f"asp_{a}" for a in ASPECTS]].values; Yte = te[[f"asp_{a}" for a in ASPECTS]].values
for col in ["text_raw", "text_norm"]:
    Xtr, Xdv, Xte = feats(col, tr, dv, te)
    for name, mk in {"LogReg": lambda c: LogisticRegression(C=c, max_iter=2000, class_weight="balanced"),
                     "LinearSVC": lambda c: LinearSVC(C=c, class_weight="balanced")}.items():
        best, bs = None, -1
        for c in ((1, 5, 20) if name == "LogReg" else (0.1, 0.3, 1.0)):
            m = OneVsRestClassifier(mk(c)).fit(Xtr, Ytr)
            s = f1_score(Ydv, m.predict(Xdv), average="micro", zero_division=0)
            if s > bs: best, bs = m, s
        pred = best.predict(Xte)
        r = {"dev_microF1": round(bs, 4), "test_microF1": round(f1_score(Yte, pred, average="micro", zero_division=0), 4),
             "test_macroF1": round(f1_score(Yte, pred, average="macro", zero_division=0), 4),
             "per_aspect_F1": {a: round(f1_score(Yte[:, i], pred[:, i], zero_division=0), 4) for i, a in enumerate(ASPECTS)}}
        RES["B_aspect_detection"][f"{name}|{col}"] = r
        print(name, col, r["test_microF1"], r["test_macroF1"])

# ---------- Task C: cảm xúc theo khía cạnh (3 lớp) – mỗi khía cạnh một bộ phân loại ----------
print("== Task C: aspect sentiment ==")
RES["C_aspect_sentiment"] = {}
for col in ["text_raw", "text_norm"]:
    Xtr, Xdv, Xte = feats(col, tr_p.drop_duplicates("index"), dv_p.drop_duplicates("index"), te_p.drop_duplicates("index")) if False else (None, None, None)
    w = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    ch = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=150000)
    w.fit(tr[col].fillna("")); ch.fit(tr[col].fillna(""))
    tf = lambda d: hstack([w.transform(d[col].fillna("")), ch.transform(d[col].fillna(""))]).tocsr()
    allp, allt = [], []
    for a in ASPECTS:
        a_tr, a_dv, a_te = (d[d.aspect == a] for d in (tr_p, dv_p, te_p))
        if len(a_te) == 0 or a_tr.polarity.nunique() < 2:
            continue
        m, _ = best_by_dev([LinearSVC(C=c, class_weight="balanced") for c in (0.1, 0.3, 1.0)],
                           tf(a_tr), a_tr.polarity, tf(a_dv) if len(a_dv) else tf(a_tr), (a_dv.polarity if len(a_dv) else a_tr.polarity),
                           lambda y, p: f1_score(y, p, average="macro"))
        allp += list(m.predict(tf(a_te))); allt += list(a_te.polarity)
    r = {"test_macroF1": round(f1_score(allt, allp, average="macro", labels=POLARITIES), 4),
         "test_acc": round(accuracy_score(allt, allp), 4), "n_pairs": len(allt),
         "per_class_F1": dict(zip(POLARITIES, np.round(f1_score(allt, allp, average=None, labels=POLARITIES), 4).tolist())),
         "confusion(rows=true,cols=pred;Neg,Neu,Pos)": confusion_matrix(allt, allp, labels=POLARITIES).tolist()}
    RES["C_aspect_sentiment"][f"per-aspect LinearSVC|{col}"] = r
    print(col, r["test_macroF1"], r["per_class_F1"])

json.dump(RES, open("results/baseline_results.json", "w"), ensure_ascii=False, indent=2)
