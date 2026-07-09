from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def summarize_cluster(cluster: List[Dict]):

    all_sentences = []

    for article in cluster:

        sentences = article["content"].replace(
            "?", "."
        ).replace(
            "!", "."
        ).split(".")

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) > 60:
                all_sentences.append(sentence)

    if len(all_sentences) < 3:
        return None

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1500,
    )

    tfidf = vectorizer.fit_transform(all_sentences)

    scores = tfidf.sum(axis=1).A1

    ranked = np.argsort(scores)[::-1]

    selected = []

    for idx in ranked:

        selected.append(all_sentences[idx])

        if len(selected) >= 4:
            break

    return " ".join(selected)