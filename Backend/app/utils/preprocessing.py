import re


def clean_text(text: str) -> str:

    if not text:
        return ""

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()