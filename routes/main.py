from flask import Blueprint, render_template
from utils import generate_csrf_token
from urllib.parse import unquote

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/survey')
def survey():
    from legacy.questions import get_gender_question, get_regular_questions
    gender_q = get_gender_question()
    regular_qs = get_regular_questions()
    return render_template('survey.html', gender_question=gender_q, questions=regular_qs, csrf_token=generate_csrf_token())

@main_bp.route('/results')
def results():
    return render_template('results.html', csrf_token=generate_csrf_token())

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/benzer/<path:name>')
def benzer(name):
    from perfume_engine import PERFUME_DATABASE, matching_engine
    from legacy.scoring import ScoringEngine
    from ml_similarity import find_similar

    decoded = unquote(name)
    perfumes = PERFUME_DATABASE
    source = next((p for p in perfumes if p['name'] == decoded), None)
    if not source:
        return render_template('results.html',
            profil_adi='Bulunamadı',
            profil_yuzde=0,
            aciklama='Parfüm bulunamadı.',
            parfumler=[],
            yetersiz_parfum=True,
            radar_labels='[]',
            radar_data='[]',
            radar_parfum='[]',
            pie_labels='[]',
            pie_data='[]',
            chart_json='')

    similar = find_similar(decoded, perfumes, top_n=9)
    if not similar:
        similar = [dict(p) for p in perfumes[:9]]
    for p in similar:
        if p['name'] == decoded and 'benzerlik_yuzde' in p:
            del p['benzerlik_yuzde']

    top_pct = source.get('profile', {}).get('top_pct', 33)
    mid_pct = source.get('profile', {}).get('middle_pct', 33)
    base_pct = source.get('profile', {}).get('base_pct', 34)

    top_notes = source.get('notes_top', [])
    if isinstance(top_notes, list): top_notes = ', '.join(top_notes[:3])
    mid_notes = source.get('notes_middle', [])
    if isinstance(mid_notes, list): mid_notes = ', '.join(mid_notes[:3])
    base_notes = source.get('notes_base', [])
    if isinstance(base_notes, list): base_notes = ', '.join(base_notes[:3])

    profile_texts = [
        f"{source['brand']} {source['name']}: Üst notaları {top_notes}, "
        f"orta notaları {mid_notes}, alt notaları {base_notes}. "
        f"{source.get('description', '')}"
    ]

    from ai_service import generate_explanations
    ai_explanations = {}
    try:
        note_profile = {
            'top_pct': top_pct, 'middle_pct': mid_pct, 'base_pct': base_pct,
            'top_dominant': 'citrus', 'middle_dominant': 'floral',
            'base_dominant': 'musk', 'profile_type': 'Koku Profili',
            'nota_detay': {'top': {}, 'middle': {}, 'base': {}}
        }
        recommendations = {'yaz': [], 'kis': [], 'dört_mevsim': [], 'profile_type': 'benzer'}
        ai_explanations = generate_explanations(note_profile, recommendations, 'unisex', decoded)
    except Exception:
        pass

    radar_labels = "['Üst Nota', 'Orta Nota', 'Alt Nota']"
    radar_data = f'[{top_pct}, {mid_pct}, {base_pct}]'
    radar_parfum = f'[{top_pct}, {mid_pct}, {base_pct}]'
    pie_labels = "['Üst Nota', 'Orta Nota', 'Alt Nota']"
    pie_data = f'[{top_pct}, {mid_pct}, {base_pct}]'

    return render_template('results.html',
        profil_adi=f"{source['brand']} {source['name']}",
        profil_yuzde=round((top_pct + mid_pct + base_pct) / 3),
        aciklama=f"{source['brand']} {source['name']} parfümüne en çok benzeyen {len(similar)} parfüm.",
        parfumler=similar,
        yetersiz_parfum=len(similar) == 0,
        radar_labels=radar_labels,
        radar_data=radar_data,
        radar_parfum=radar_parfum,
        pie_labels=pie_labels,
        pie_data=pie_data,
        chart_json='')
