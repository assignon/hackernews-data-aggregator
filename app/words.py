import re
from collections import Counter
from bs4 import BeautifulSoup
from app.config import STOPWORDS

def extract_words(html_text: str) -> list[str]:
    if not html_text:
        return []
    plain = BeautifulSoup(html_text, "html.parser").get_text()
    plain  = plain.lower()
    tokens = re.findall(r"\b[a-z]{2,}\b", plain)
    return [t for t in tokens if t not in STOPWORDS]

def top_n_words(texts: list[str], n: int = 10) -> list[tuple[str, int]]:
    counter = Counter()
    for text in texts:
        counter.update(extract_words(text))
    return counter.most_common(n)
