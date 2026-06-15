# ParfumAI — Cosine Similarity Engine
# Copyright (c) 2026 Ahmet Rıfai Kuyucu

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MATRIX_PATH = os.path.join(DATA_DIR, 'similarity_matrix.pkl')
VECTORIZER_PATH = os.path.join(DATA_DIR, 'vectorizer.pkl')
PERFUME_IDS_PATH = os.path.join(DATA_DIR, 'perfume_ids.pkl')


def clear_cache():
    for path in (MATRIX_PATH, VECTORIZER_PATH, PERFUME_IDS_PATH):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

def build_note_text(perfume):
    notes = []
    for key in ('notes_top', 'notes_middle', 'notes_base'):
        vals = perfume.get(key, [])
        if isinstance(vals, list):
            notes.extend(vals)
        elif isinstance(vals, str):
            notes.extend([n.strip() for n in vals.split(',') if n.strip()])
    return ' '.join(notes)


def precompute_similarity(perfumes):
    texts = [build_note_text(p) for p in perfumes]
    vectorizer = CountVectorizer(analyzer='word', token_pattern=r'(?u)\b\w+\b', lowercase=True)
    X = vectorizer.fit_transform(texts)
    matrix = cosine_similarity(X, X)
    perfume_ids = [p.get('id', p['name']) for p in perfumes]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MATRIX_PATH, 'wb') as f:
        pickle.dump(matrix, f)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(PERFUME_IDS_PATH, 'wb') as f:
        pickle.dump(perfume_ids, f)

    return matrix, vectorizer, perfume_ids


def load_similarity():
    if not all(os.path.exists(p) for p in (MATRIX_PATH, VECTORIZER_PATH, PERFUME_IDS_PATH)):
        return None, None, None
    with open(MATRIX_PATH, 'rb') as f:
        matrix = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(PERFUME_IDS_PATH, 'rb') as f:
        perfume_ids = pickle.load(f)
    return matrix, vectorizer, perfume_ids


def find_similar(perfume_name, perfumes, top_n=10):
    matrix, vectorizer, perfume_ids = load_similarity()
    if matrix is None:
        matrix, vectorizer, perfume_ids = precompute_similarity(perfumes)

    if perfume_name not in perfume_ids:
        matched = [p for p in perfumes if p['name'] == perfume_name]
        if not matched:
            return []
        idx = perfume_ids.index(matched[0].get('id', matched[0]['name']))
    else:
        idx = perfume_ids.index(perfume_name)

    scores = list(enumerate(matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    results = []
    for i, score in scores[1:top_n + 1]:
        if i < len(perfumes):
            p = dict(perfumes[i])
            p['benzerlik_yuzde'] = round(score * 100, 1)
            results.append(p)
    return results


def compute_jaccard_similarity(user_notes, perfume):
    if not user_notes or not isinstance(user_notes, (set, list)):
        return 0.0

    user_set = set(n.lower().replace(' ', '_') for n in user_notes)

    perfume_set = set()
    for key in ('notes_top', 'notes_middle', 'notes_base'):
        vals = perfume.get(key, [])
        if isinstance(vals, list):
            perfume_set.update(v.lower().replace(' ', '_') for v in vals)
        elif isinstance(vals, str):
            perfume_set.update(v.strip().lower().replace(' ', '_') for v in vals.split(',') if v.strip())

    intersection = user_set & perfume_set
    union = user_set | perfume_set
    if not union:
        return 0.0
    return round(len(intersection) / len(union), 4)
