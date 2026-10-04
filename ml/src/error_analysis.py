import sys, pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
tr, te = pd.read_csv("processed/train.csv"), pd.read_csv("processed/test.csv")
w = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True); ch = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=150000)
X = hstack([w.fit_transform(tr.text_norm), ch.fit_transform(tr.text_norm)]).tocsr()
m = LogisticRegression(C=5, max_iter=2000, class_weight="balanced").fit(X, tr.has_negative)
Xt = hstack([w.transform(te.text_norm), ch.transform(te.text_norm)]).tocsr()
te["pred"] = m.predict(Xt); te["p_neg"] = m.predict_proba(Xt)[:, 1]
err = te[te.pred != te.has_negative].copy()
err["error_type"] = err.apply(lambda r: "FN (bỏ sót tiêu cực)" if r.has_negative == 1 else "FP (báo nhầm tiêu cực)", axis=1)
err["len"] = err.comment.str.len()
print(err.error_type.value_counts().to_string())
print("Sai nhiều nhất theo số sao:\n", err.groupby("n_star").size().to_string())
err[["comment", "n_star", "label", "has_negative", "pred", "p_neg", "error_type"]].sort_values("p_neg").to_csv("results/error_analysis_taskA.csv", index=False)
fn = err[err.has_negative == 1].head(5)
for _, r in fn.iterrows(): print("-", r.comment[:140], "|", r.label)
