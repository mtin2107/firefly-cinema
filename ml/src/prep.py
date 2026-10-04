"""Tạo dữ liệu đã xử lý (train/dev/test) và thống kê mô tả cho báo cáo."""
import sys, json
import pandas as pd
sys.path.insert(0, "src")
from common import load_split, ASPECTS

D = "UIT-ViSFD-main/data"
out = {}
for s in ["Train", "Dev", "Test"]:
    df = load_split(D, s)
    df.drop(columns=["aspects"]).to_csv(f"processed/{s.lower()}.csv", index=False)
    long = []
    for _, r in df.iterrows():
        for a, p in r["aspects"].items():
            long.append({"index": r["index"], "aspect": a, "polarity": p,
                         "text_norm": r["text_norm"], "text_raw": r["text_raw"]})
    pd.DataFrame(long).to_csv(f"processed/{s.lower()}_aspect_sentiment.csv", index=False)
    out[s] = {
        "n_comments": len(df),
        "overall_dist": df["overall"].value_counts().to_dict(),
        "has_negative_rate": round(df["has_negative"].mean(), 4),
        "avg_aspects_per_comment": round(df[[f"asp_{a}" for a in ASPECTS]].sum(axis=1).mean(), 3),
        "n_aspect_sentiment_pairs": len(long),
        "pair_polarity_dist": pd.DataFrame(long)["polarity"].value_counts().to_dict(),
        "aspect_dist": {a: int(df[f"asp_{a}"].sum()) for a in ASPECTS},
    }
json.dump(out, open("results/dataset_stats.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=1))
