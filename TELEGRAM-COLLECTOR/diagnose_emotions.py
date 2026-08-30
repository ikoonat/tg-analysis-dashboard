"""Check every configured language lexicon and its emotion coverage."""

import os
import re

import pandas as pd

from config import Config
from sentiment_analyzer import SentimentAnalyzer


def print_lexicon_status(analyzer):
    """Report loaded word and emotion counts for every configured language."""
    print("=" * 70)
    print("LEXICON STATUS")
    print("=" * 70)

    for language in sorted(analyzer.lexicons):
        lexicon = analyzer.lexicons[language]
        emotion_count = sum(len(emotions) for emotions in lexicon.values())
        print(
            f"{language:12} words={len(lexicon):6} "
            f"emotion_labels={emotion_count:6} "
            f"stopwords={len(analyzer.stopwords.get(language, set())):6}"
        )
        if lexicon:
            print(f"  sample: {list(lexicon.items())[:3]}")
        else:
            print("  WARNING: no words loaded")


def check_lexicon_format(config):
    """Check the configured lexicon files and describe their detected format."""
    print("\n" + "=" * 70)
    print("LEXICON FILE CHECK")
    print("=" * 70)

    for language in sorted(config.LANGUAGE_LEXICONS):
        path = config.LANGUAGE_LEXICONS[language]
        print(f"\n{language}: {path}")

        if not os.path.exists(path):
            print("  ERROR: file not found")
            continue

        with open(path, "r", encoding="utf-8") as file:
            lines = [line.rstrip("\n") for line in file]

        data_lines = [line for line in lines[1:] if line.strip()]
        if not data_lines:
            print("  WARNING: file has no data rows")
            continue

        columns = len(data_lines[0].split("\t"))
        if columns >= 12:
            format_name = "matrix (12+ columns)"
        elif columns >= 3:
            format_name = "standard (3+ columns)"
        else:
            format_name = f"unexpected ({columns} columns)"
        print(f"  OK: {len(data_lines)} data rows, {format_name}")


def test_loaded_lexicons(analyzer):
    """Smoke-test word and emotion loading for every language."""
    print("\n" + "=" * 70)
    print("ALL LANGUAGE LEXICON TEST")
    print("=" * 70)

    for language in sorted(analyzer.lexicons):
        lexicon = analyzer.lexicons[language]
        if not lexicon:
            print(f"{language:12} FAIL: no words loaded")
            continue

        sample_words = list(lexicon)[:5]
        emotion_labels = [label for word in sample_words for label in lexicon[word]]
        print(
            f"{language:12} OK: {len(sample_words)} sample words, "
            f"{len(emotion_labels)} emotion labels"
        )
        print(f"  words: {sample_words}")


def diagnose_messages(analyzer):
    """Analyze up to five saved messages for each language present in the data."""
    print("\n" + "=" * 70)
    print("SAVED MESSAGE TEST")
    print("=" * 70)

    path = os.path.join("output", "messages_data.csv")
    if not os.path.exists(path):
        print(f"No saved message file found at {path}")
        return

    data = pd.read_csv(path, encoding="utf-8-sig")
    if "Language" not in data or "Message_Text" not in data:
        print("ERROR: messages_data.csv needs Language and Message_Text columns")
        return

    languages = sorted(
        set(data["Language"].dropna().astype(str).str.lower())
        & set(analyzer.lexicons)
    )
    if not languages:
        print("No languages in the saved data match the configured lexicons")
        return

    for language in languages:
        print(f"\n{language.upper()}: up to 5 messages")
        messages = data[data["Language"].astype(str).str.lower() == language].head(5)
        for _, row in messages.iterrows():
            text = str(row["Message_Text"])
            clean_text = re.sub(r"https?://\S+|www\.\S+|t\.me/\S+", "", text)
            result = analyzer.analyze_sentiment(clean_text)
            matched_words = [
                token
                for token in result["tokens"]
                if token in analyzer.lexicons[result["language"]]
            ]
            print(
                f"  detected={result['language']} "
                f"tokens={len(result['tokens'])} "
                f"matches={len(matched_words)} "
                f"dominant={result['dominant_emotion']}"
            )
            print(f"  text: {text[:160]}")


def show_emotion_coverage(analyzer):
    """Show counts for the standard emotion labels in every language."""
    print("\n" + "=" * 70)
    print("EMOTION COVERAGE")
    print("=" * 70)

    emotions = [
        "anger",
        "anticipation",
        "disgust",
        "fear",
        "joy",
        "negative",
        "positive",
        "sadness",
        "surprise",
        "trust",
    ]
    for language in sorted(analyzer.lexicons):
        lexicon = analyzer.lexicons[language]
        counts = {
            emotion: sum(emotion in labels for labels in lexicon.values())
            for emotion in emotions
        }
        summary = ", ".join(f"{emotion}={count}" for emotion, count in counts.items())
        print(f"{language:12} {summary}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    config = Config()
    analyzer = SentimentAnalyzer(config)
    print_lexicon_status(analyzer)
    check_lexicon_format(config)
    test_loaded_lexicons(analyzer)
    show_emotion_coverage(analyzer)
    diagnose_messages(analyzer)


if __name__ == "__main__":
    main()
