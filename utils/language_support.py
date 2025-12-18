# utils/language_support.py

from deep_translator import GoogleTranslator

SUPPORTED_LANGS = ["en", "hi", "mr", "ta", "te", "bn"]

def detect_language(text: str) -> str:
    """
    Very lightweight language detection based on script.
    Enough for Indian languages demo.
    """
    for ch in text:
        if "\u0900" <= ch <= "\u097F":
            return "hi"   # Hindi / Devanagari
        if "\u0A80" <= ch <= "\u0AFF":
            return "gu"
        if "\u0B80" <= ch <= "\u0BFF":
            return "ta"
        if "\u0C00" <= ch <= "\u0C7F":
            return "te"
    return "en"


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text

    try:
        return GoogleTranslator(
            source=source_lang,
            target="en"
        ).translate(text)
    except Exception:
        return text


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text

    try:
        return GoogleTranslator(
            source="en",
            target=target_lang
        ).translate(text)
    except Exception:
        return text
