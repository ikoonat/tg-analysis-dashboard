import pandas as pd
import re
import unicodedata

# ----------------------------
# Hebrew normalization rules
# ----------------------------

FINAL_LETTERS = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ"
}

PREFIXES = ("ו", "ה", "ל", "ב", "כ", "מ", "ש")

def normalize_hebrew(text):
    if not isinstance(text, str):
        return ""

    # Remove niqqud
    text = ''.join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

    # Normalize final letters
    for final, normal in FINAL_LETTERS.items():
        text = text.replace(final, normal)

    # Normalize quotes
    text = text.replace("״", '"').replace("׳", "'")

    # Remove punctuation
    text = re.sub(r"[^\u0590-\u05FF\s]", "", text)

    return text.strip()

def strip_prefix(word):
    while word.startswith(PREFIXES) and len(word) > 2:
        word = word[1:]
    return word

# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    INPUT_CSV = "hebrew_lexicon.csv"     # <-- your input
    OUTPUT_CSV = "hebrew_lexicon_normalized.csv"

    df = pd.read_csv(INPUT_CSV)

    if "Hebrew Word" not in df.columns:
        raise ValueError("Expected column 'Hebrew Word' not found")

    df["normalized"] = (
        df["Hebrew Word"]
        .apply(normalize_hebrew)
        .apply(strip_prefix)
    )

    # Remove only empty normalized forms
    df = df[df["normalized"] != ""]

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("✔ Lexicon normalization complete")
    print("→ Output:", OUTPUT_CSV)
