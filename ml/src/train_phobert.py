"""Fine-tune PhoBERT trên UIT-ViSFD cho 3 bài toán. CHẠY TRÊN GOOGLE COLAB (GPU T4 là đủ).

Cài đặt (ô đầu của notebook):
    !pip -q install transformers datasets accelerate underthesea scikit-learn pandas
Chạy ví dụ:
    !python train_phobert.py --task A --data_dir processed --out_dir out_A
    !python train_phobert.py --task B --data_dir processed --out_dir out_B
    !python train_phobert.py --task C --data_dir processed --out_dir out_C
Task A: bình luận có ý kiến tiêu cực (nhị phân)   Task B: phát hiện 10 khía cạnh (đa nhãn)
Task C: cảm xúc 3 lớp theo khía cạnh (đầu vào là cặp: tên khía cạnh + bình luận)
"""
import argparse, json, os
import numpy as np, pandas as pd, torch
from sklearn.metrics import f1_score, accuracy_score
from transformers import (AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments,
                          Trainer, DataCollatorWithPadding, EarlyStoppingCallback)
from underthesea import word_tokenize

ASPECTS = ["SCREEN", "CAMERA", "FEATURES", "BATTERY", "PERFORMANCE", "STORAGE", "DESIGN", "PRICE", "GENERAL", "SER&ACC"]
POL = ["Negative", "Neutral", "Positive"]
ap = argparse.ArgumentParser()
ap.add_argument("--task", choices=["A", "B", "C"], required=True)
ap.add_argument("--data_dir", default="processed")
ap.add_argument("--out_dir", default="out")
ap.add_argument("--model", default="vinai/phobert-base-v2")
ap.add_argument("--epochs", type=int, default=6)
ap.add_argument("--lr", type=float, default=3e-5)
ap.add_argument("--bs", type=int, default=32)
ap.add_argument("--max_len", type=int, default=160)
ap.add_argument("--seed", type=int, default=42)
args = ap.parse_args()
torch.manual_seed(args.seed); np.random.seed(args.seed)

seg = lambda s: word_tokenize(str(s), format="text")   # PhoBERT cần văn bản đã tách từ
tok = AutoTokenizer.from_pretrained(args.model)


def load(split):
    if args.task == "C":
        d = pd.read_csv(f"{args.data_dir}/{split}_aspect_sentiment.csv")
        d["label"] = d.polarity.map({p: i for i, p in enumerate(POL)})
        d["a"] = d.aspect.str.lower()
    else:
        d = pd.read_csv(f"{args.data_dir}/{split}.csv")
        d["label"] = d.has_negative if args.task == "A" else d[[f"asp_{a}" for a in ASPECTS]].values.astype("float32").tolist()
    d["t"] = d.text_norm.fillna("").map(seg)
    return d


class DS(torch.utils.data.Dataset):
    def __init__(self, d): self.d = d.reset_index(drop=True)
    def __len__(self): return len(self.d)
    def __getitem__(self, i):
        r = self.d.iloc[i]
        enc = tok(r.a, r.t, truncation=True, max_length=args.max_len) if args.task == "C" else tok(r.t, truncation=True, max_length=args.max_len)
        enc["labels"] = r.label
        return enc


tr, dv, te = load("train"), load("dev"), load("test")
nl = {"A": 2, "B": len(ASPECTS), "C": 3}[args.task]
model = AutoModelForSequenceClassification.from_pretrained(
    args.model, num_labels=nl, problem_type="multi_label_classification" if args.task == "B" else "single_label_classification")


def metrics(p):
    lg, y = p
    if args.task == "B":
        pr = (1 / (1 + np.exp(-lg)) > 0.5).astype(int); y = np.array(y)
        return {"micro_f1": f1_score(y, pr, average="micro", zero_division=0), "macro_f1": f1_score(y, pr, average="macro", zero_division=0)}
    pr = lg.argmax(-1)
    return {"macro_f1": f1_score(y, pr, average="macro"), "acc": accuracy_score(y, pr)}


targs = TrainingArguments(output_dir=args.out_dir, num_train_epochs=args.epochs, learning_rate=args.lr,
                          per_device_train_batch_size=args.bs, per_device_eval_batch_size=64, eval_strategy="epoch",
                          save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="macro_f1" if args.task != "B" else "micro_f1",
                          warmup_ratio=0.1, weight_decay=0.01, fp16=torch.cuda.is_available(), seed=args.seed,
                          save_total_limit=1, report_to="none", logging_steps=50)
trainer = Trainer(model=model, args=targs, train_dataset=DS(tr), eval_dataset=DS(dv), data_collator=DataCollatorWithPadding(tok),
                  compute_metrics=metrics, callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
trainer.train()
res = {"task": args.task, "model": args.model, "dev": trainer.evaluate(DS(dv)), "test": trainer.predict(DS(te)).metrics}
os.makedirs(args.out_dir, exist_ok=True)
json.dump(res, open(f"{args.out_dir}/phobert_results.json", "w"), indent=2)
trainer.save_model(f"{args.out_dir}/best"); tok.save_pretrained(f"{args.out_dir}/best")
print(json.dumps(res, indent=2))
