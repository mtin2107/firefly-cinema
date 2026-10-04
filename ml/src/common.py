"""Tiện ích dùng chung: đọc ViSFD, tách nhãn, chuẩn hóa văn bản mạng xã hội tiếng Việt."""
import re
import pandas as pd

ASPECTS = ["SCREEN", "CAMERA", "FEATURES", "BATTERY", "PERFORMANCE",
           "STORAGE", "DESIGN", "PRICE", "GENERAL", "SER&ACC"]
POLARITIES = ["Negative", "Neutral", "Positive"]
TAG_RE = re.compile(r"\{([A-Z&]+)(?:#(Positive|Negative|Neutral))?\}")

# Từ điển teencode/viết tắt nhỏ (mở rộng dần khi phân tích lỗi)
TEENCODE = {
    "ko": "không", "k": "không", "kh": "không", "khong": "không", "hok": "không", "hông": "không",
    "dc": "được", "đc": "được", "duoc": "được", "dk": "được",
    "sp": "sản phẩm", "đt": "điện thoại", "dt": "điện thoại", "mn": "mọi người",
    "wf": "wifi", "wifi": "wifi", "sài": "xài", "ok": "ổn", "oke": "ổn", "okie": "ổn",
    "bt": "bình thường", "bthg": "bình thường", "vs": "với", "j": "gì", "z": "vậy",
    "tg": "thời gian", "nv": "nhân viên", "tgdd": "thegioididong", "cx": "cũng",
    "m": "mình", "mk": "mình", "mik": "mình", "r": "rồi", "ròi": "rồi", "lun": "luôn",
    "thik": "thích", "thich": "thích", "tks": "cảm ơn", "thanks": "cảm ơn",
}


def parse_label(label: str):
    """'{BATTERY#Negative};{OTHERS};' -> ({'BATTERY': 'Negative'}, has_others)"""
    asp, others = {}, False
    for a, p in TAG_RE.findall(str(label)):
        if a == "OTHERS" or not p:
            others = True
        else:
            asp[a] = p
    return asp, others


def normalize(text: str, teencode: bool = True) -> str:
    t = str(text).lower()
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)            # "tốtttt" -> "tốtt"
    t = re.sub(r"([!?.,])\1+", r"\1", t)            # "!!!" -> "!"
    t = re.sub(r"([,.!?;:()\-/])", r" \1 ", t)      # tách dấu câu
    toks = t.split()
    if teencode:
        toks = [TEENCODE.get(w, w) for w in toks]
    return " ".join(toks)


def load_split(path_dir: str, split: str) -> pd.DataFrame:
    df = pd.read_csv(f"{path_dir}/{split}.csv")
    parsed = df["label"].apply(parse_label)
    df["aspects"] = parsed.apply(lambda x: x[0])
    df["has_others"] = parsed.apply(lambda x: x[1])
    for a in ASPECTS:
        df[f"asp_{a}"] = df["aspects"].apply(lambda d, a=a: int(a in d))
    pols = df["aspects"].apply(lambda d: set(d.values()))
    df["has_negative"] = pols.apply(lambda s: int("Negative" in s))
    # Cảm xúc tổng thể: ưu tiên tiêu cực > tích cực > trung lập/không rõ
    df["overall"] = pols.apply(lambda s: "Negative" if "Negative" in s else
                               ("Positive" if "Positive" in s else "Neutral"))
    df["text_norm"] = df["comment"].apply(normalize)
    df["text_raw"] = df["comment"].astype(str)
    return df
