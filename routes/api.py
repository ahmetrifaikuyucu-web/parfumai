from flask import Blueprint, render_template, request, jsonify, session
from utils import generate_csrf_token, csrf_required, login_required
from scoring import ScoringEngine, NOTE_CATEGORIES
from perfume_engine import matching_engine, _init_database, save_database, _write_audit, check_critical_stock
from ai_service import generate_explanations
import json
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/submit', methods=['POST'])
@csrf_required
def submit_survey():
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        gender_raw = data.get('gender', 'unisex')
        gender = 'unisex'
        normalized = gender_raw.lower().strip()
        if normalized in ['kadin', 'kad\u0131n', 'female', 'woman']:
            gender = 'kad\u0131n'
        elif normalized in ['erkek', 'male', 'man']:
            gender = 'erkek'
        name = data.get('name', 'Misafir')

        note_profile = ScoringEngine().process_answers(answers)
        recommendations = matching_engine.find_matches(note_profile, gender)

        ai_explanations = {}
        try:
            ai_explanations = generate_explanations(note_profile, recommendations, gender, name)
        except Exception as e:
            print(f"[AI] A\u00e7\u0131klama \u00fcretilemedi: {e}")

        def clean_perfume(p):
            return {
                'name': p['name'],
                'brand': p['brand'],
                'season': p['season'],
                'gender': p['gender'],
                'description': p['description'],
                'price_range': p['price_range'],
                'notes_top': p['notes_top'],
                'notes_middle': p['notes_middle'],
                'notes_base': p['notes_base'],
                'in_stock': p.get('in_stock', True),
                'image_url': p.get('image_url', '')
            }

        return jsonify({
            'success': True,
            'gender': gender,
            'note_profile': {
                'top_pct': note_profile['top_pct'],
                'middle_pct': note_profile['middle_pct'],
                'base_pct': note_profile['base_pct'],
                'top_dominant': note_profile['top_dominant'],
                'middle_dominant': note_profile['middle_dominant'],
                'base_dominant': note_profile['base_dominant'],
                'profile_type': note_profile['profile_type'],
                'nota_detay': note_profile['nota_detay']
            },
            'recommendations': {
                'yaz': [clean_perfume(p) for p in recommendations['yaz'][:3]],
                'kis': [clean_perfume(p) for p in recommendations['kis'][:3]],
                'd\u00f6rt_mevsim': [clean_perfume(p) for p in recommendations['d\u00f6rt_mevsim'][:3]],
                'profile_type': recommendations['profile_type']
            },
            'ai_explanations': ai_explanations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/api/questions')
def get_questions():
    from questions import get_gender_question, get_regular_questions
    gender_q = get_gender_question()
    regular_qs = get_regular_questions()
    return jsonify({"gender": gender_q, "regular": regular_qs})

@api_bp.route('/api/node_categories')
def get_note_categories():
    return jsonify(NOTE_CATEGORIES)

@api_bp.route('/api/stock')
def get_stock():
    from perfume_engine import PERFUME_DATABASE
    stock = {}
    for p in PERFUME_DATABASE:
        stock[p['name']] = {
            'in_stock': p.get('in_stock', True),
            'price_range': p.get('price_range', '')
        }
    return jsonify(stock)

@api_bp.route('/api/explain', methods=['POST'])
def api_explain():
    try:
        data = request.get_json()
        perfumes = data.get('perfumes', []) if isinstance(data, dict) else []
        note_profile = data.get('note_profile', {}) if isinstance(data, dict) else data
        if isinstance(note_profile, str):
            try: note_profile = json.loads(note_profile)
            except: note_profile = {}
        gender = data.get('gender', 'unisex') if isinstance(data, dict) else 'unisex'
        name = data.get('name', 'Misafir') if isinstance(data, dict) else 'Misafir'

        recommendations = matching_engine.find_matches(note_profile, gender)
        explanations = generate_explanations(note_profile, recommendations, gender, name)

        result = {}
        for p in perfumes:
            if p in explanations:
                result[p] = explanations[p]

        return jsonify({'success': True, 'explanations': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/api/log-sale', methods=['POST'])
@csrf_required
def log_sale():
    try:
        data = request.get_json()
        import csv
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sales_log.csv')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_exists = os.path.exists(log_path)
        with open(log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'customer_name', 'recommended', 'purchased', 'amount'])
            writer.writerow([
                data.get('timestamp', ''),
                data.get('customer_name', ''),
                data.get('recommended', ''),
                data.get('purchased', ''),
                data.get('amount', '')
            ])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
