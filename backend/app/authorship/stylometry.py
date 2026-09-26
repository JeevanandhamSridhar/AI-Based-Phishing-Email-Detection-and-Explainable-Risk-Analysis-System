"""Stylometric Feature Extractor for AI Authorship Estimation

Extracts structural, lexical, syntactic, and readability markers from text.
Follows the stylometric methodology inspired by Opara et al. (2025).
"""

import math
import re
from typing import Dict, List, Tuple
import numpy as np
import textstat

# Formal connectives frequently favored by modern LLM language generation
FORMAL_CONNECTIVES = {
    "furthermore", "moreover", "consequently", "therefore", "additionally",
    "specifically", "regarding", "accordingly", "subsequently", "nevertheless",
    "in order to", "as a result", "in accordance with", "please be advised",
    "kindly ensure", "we appreciate your", "sincerely"
}

# Informal colloquialisms and typos common in human-crafted spam/phishing
INFORMAL_MARKERS = {
    "u", "ur", "pls", "plz", "asap", "gonna", "wanna", "thx", "dear customer",
    "clickk", "act now!!", "hurry!!", "won!", "winner!!"
}

FEATURE_NAMES = [
    "type_token_ratio",
    "hapax_legomena_ratio",
    "avg_sentence_length",
    "sentence_length_variance",
    "avg_word_length",
    "exclamation_density",
    "question_density",
    "comma_density",
    "semicolon_density",
    "uppercase_ratio",
    "digit_density",
    "flesch_reading_ease",
    "flesch_kincaid_grade",
    "formal_connective_density",
    "informal_marker_density",
    "paragraph_count",
    "avg_characters_per_sentence",
    "lexical_density",
]


def extract_stylometric_features(text: str) -> Tuple[np.ndarray, Dict[str, float]]:
    """Extracts an 18-dimensional stylometric feature vector and dictionary from text."""
    clean_text = text.strip()
    if not clean_text:
        zero_arr = np.zeros(len(FEATURE_NAMES), dtype=np.float32)
        zero_dict = {name: 0.0 for name in FEATURE_NAMES}
        return zero_arr, zero_dict

    total_chars = len(clean_text)
    words = re.findall(r"\b[a-zA-Z0-9']+\b", clean_text)
    total_words = len(words) if words else 1
    lower_words = [w.lower() for w in words]

    # Sentence extraction
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    sentence_count = len(sentences) if sentences else 1

    # 1. Lexical Diversity
    unique_words = set(lower_words)
    type_token_ratio = len(unique_words) / total_words

    word_counts = {}
    for w in lower_words:
        word_counts[w] = word_counts.get(w, 0) + 1
    hapax_count = sum(1 for w, c in word_counts.items() if c == 1)
    hapax_legomena_ratio = hapax_count / total_words

    # 2. Sentence Length Mean & Variance
    sentence_lengths = [len(re.findall(r"\b[a-zA-Z0-9']+\b", s)) for s in sentences]
    avg_sentence_length = float(np.mean(sentence_lengths)) if sentence_lengths else 0.0
    sentence_length_variance = float(np.std(sentence_lengths)) if sentence_lengths else 0.0

    # 3. Word Length
    word_lengths = [len(w) for w in words]
    avg_word_length = float(np.mean(word_lengths)) if word_lengths else 0.0

    # 4. Punctuation & Character Distributions
    exclamation_density = (clean_text.count("!") / total_chars) * 100.0
    question_density = (clean_text.count("?") / total_chars) * 100.0
    comma_density = (clean_text.count(",") / total_chars) * 100.0
    semicolon_density = (clean_text.count(";") / total_chars) * 100.0

    alpha_chars = sum(1 for c in clean_text if c.isalpha())
    upper_chars = sum(1 for c in clean_text if c.isupper())
    uppercase_ratio = (upper_chars / alpha_chars) if alpha_chars > 0 else 0.0
    digit_density = (sum(1 for c in clean_text if c.isdigit()) / total_chars) * 100.0

    # 5. Readability Metrics
    try:
        flesch_reading_ease = float(textstat.flesch_reading_ease(clean_text))
    except Exception:
        flesch_reading_ease = 60.0

    try:
        flesch_kincaid_grade = float(textstat.flesch_kincaid_grade(clean_text))
    except Exception:
        flesch_kincaid_grade = 8.0

    # 6. Specific Stylistic Dictionaries
    formal_matches = sum(1 for w in lower_words if w in FORMAL_CONNECTIVES)
    formal_connective_density = (formal_matches / total_words) * 100.0

    informal_matches = sum(1 for w in lower_words if w in INFORMAL_MARKERS)
    informal_marker_density = (informal_matches / total_words) * 100.0

    # 7. Structural Layout
    paragraphs = [p for p in clean_text.split("\n\n") if p.strip()]
    paragraph_count = float(len(paragraphs)) if paragraphs else 1.0
    avg_chars_per_sentence = total_chars / sentence_count

    # 8. Lexical Density
    lexical_density = len(unique_words) / math.sqrt(total_words) if total_words > 0 else 0.0

    feature_dict = {
        "type_token_ratio": round(type_token_ratio, 4),
        "hapax_legomena_ratio": round(hapax_legomena_ratio, 4),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "sentence_length_variance": round(sentence_length_variance, 2),
        "avg_word_length": round(avg_word_length, 2),
        "exclamation_density": round(exclamation_density, 4),
        "question_density": round(question_density, 4),
        "comma_density": round(comma_density, 4),
        "semicolon_density": round(semicolon_density, 4),
        "uppercase_ratio": round(uppercase_ratio, 4),
        "digit_density": round(digit_density, 4),
        "flesch_reading_ease": round(flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
        "formal_connective_density": round(formal_connective_density, 4),
        "informal_marker_density": round(informal_marker_density, 4),
        "paragraph_count": paragraph_count,
        "avg_characters_per_sentence": round(avg_chars_per_sentence, 2),
        "lexical_density": round(lexical_density, 2),
    }

    feature_vector = np.array([feature_dict[name] for name in FEATURE_NAMES], dtype=np.float32)
    return feature_vector, feature_dict
