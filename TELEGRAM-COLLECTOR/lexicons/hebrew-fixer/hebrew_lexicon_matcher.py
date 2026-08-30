import pandas as pd
import re
import unicodedata
from rapidfuzz import fuzz, process

# ----------------------------
# Hebrew normalization
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

    # Remove punctuation (keep Hebrew letters & spaces)
    text = re.sub(r"[^\u0590-\u05FF\s]", "", text)

    return text.strip()

def strip_prefix(word):
    while word.startswith(PREFIXES) and len(word) > 2:
        word = word[1:]
    return word

# ----------------------------
# Load lexicon
# ----------------------------

def load_lexicon(path):
    lex = pd.read_csv(path)

    lex["norm"] = (
        lex["Hebrew Word"]
        .apply(normalize_hebrew)
        .apply(strip_prefix)
    )

    lex = lex.drop_duplicates("norm")
    lex = lex.set_index("norm")

    return lex

# ----------------------------
# Tokenization
# ----------------------------

def tokenize_hebrew(text):
    text = normalize_hebrew(text)
    tokens = text.split()
    tokens = [strip_prefix(t) for t in tokens if len(t) > 1]
    return tokens

# ----------------------------
# Matching
# ----------------------------

def match_word(word, lexicon, threshold=90):
    if word in lexicon.index:
        return word

    match = process.extractOne(
        word,
        lexicon.index,
        scorer=fuzz.ratio
    )

    if match and match[1] >= threshold:
        return match[0]

    return None

# ----------------------------
# Process text CSV
# ----------------------------

def process_texts(text_csv, lexicon, text_column="text"):
    df = pd.read_csv(text_csv)

    emotion_cols = [
        "anger", "anticipation", "disgust", "fear",
        "joy", "negative", "positive",
        "sadness", "surprise", "trust"
    ]

    for col in emotion_cols:
        df[col] = 0

    for idx, row in df.iterrows():
        text = str(row.get(text_column, ""))
        tokens = tokenize_hebrew(text)

        for token in tokens:
            match = match_word(token, lexicon)
            if match:
                for col in emotion_cols:
                    df.at[idx, col] += int(lexicon.loc[match][col])

    return df

# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    LEXICON_PATH = "hebrew_lexicon.csv"
    TEXT_PATH = "telegram_texts.csv"
    OUTPUT_PATH = "matched_output.csv"

    TEXT_COLUMN_NAME = "text"  # <-- change if needed

    lexicon = load_lexicon(LEXICON_PATH)
    result = process_texts(TEXT_PATH, lexicon, TEXT_COLUMN_NAME)

    result.to_csv(OUTPUT_PATH, index=False)
    print("✔ Matching complete →", OUTPUT_PATH)
