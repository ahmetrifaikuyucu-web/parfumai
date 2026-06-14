from flask import Blueprint, render_template, request, jsonify, session
from utils import generate_csrf_token, csrf_required, login_required
from scoring import ScoringEngine, NOTE_CATEGORIES
from perfume_engine import matching_engine, _init_database, save_database, _write_audit, check_critical_stock
from ai_service import generate_explanations
from ml_similarity import compute_jaccard_similarity
import json
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/submit', methods=['POST'])
@csrf_required
def submit_survey():
    try:
        data = request.get_json()
        gender_raw = data.get('gender', 'unisex')
        gender = 'unisex'
        normalized = gender_raw.lower().strip()
        if normalized in ['kadin', 'kad\u0131n', 'female', 'woman']:
            gender = 'kad\u0131n'
        elif normalized in ['erkek', 'male', 'man']:
            gender = 'erkek'
        name = data.get('name', 'Misafir')

        selected_notes = data.get('notes', [])
        selected_keywords = data.get('keywords', [])
        selected_themes = data.get('themes', [])

        keyword_note_map = {
            'sweet': ['vanilla', 'caramel', 'praline', 'sugar', 'honey', 'cotton_candy'],
            'fresh': ['bergamot', 'lemon', 'grapefruit', 'orange', 'lime', 'mandarin', 'mint', 'green'],
            'warm': ['amber', 'vanilla', 'tonka', 'cinnamon', 'benzoin', 'sandalwood'],
            'elegant': ['rose', 'jasmine', 'iris', 'violet', 'peony', 'orchid'],
            'sexy': ['musk', 'amber', 'leather', 'oud', 'tuberose', 'ylang'],
            'mysterious': ['oud', 'incense', 'patchouli', 'labdanum', 'myrrh', 'olibanum'],
            'feminine': ['rose', 'jasmine', 'vanilla', 'peony', 'gardenia', 'tuberose'],
            'masculine': ['leather', 'vetiver', 'cedar', 'tobacco', 'oakmoss', 'pine'],
            'clean': ['musk', 'soap', 'aldehyde', 'cotton', 'white_musk'],
            'classy': ['iris', 'violet', 'rose', 'sandalwood', 'champaca'],
            'soft': ['musk', 'vanilla', 'almond', 'heliotrope', 'powdery'],
            'lovely': ['strawberry', 'peach', 'vanilla', 'freesia', 'lily'],
            'lively': ['grapefruit', 'lemon', 'orange', 'ginger', 'bergamot'],
            'refreshing': ['mint', 'eucalyptus', 'sea', 'aqua', 'ozone', 'cucumber'],
            'summer': ['bergamot', 'lemon', 'coconut', 'sea', 'marine', 'pineapple'],
            'winter': ['vanilla', 'amber', 'tobacco', 'leather', 'oud', 'cinnamon'],
            'grass': ['green', 'grass', 'fig_leaf', 'violet_leaf', 'stem'],
            'plants': ['green', 'herbal', 'basil', 'rosemary', 'sage', 'thyme'],
            'luxury': ['oud', 'saffron', 'rose', 'leather', 'amber', 'incense'],
            'mature': ['leather', 'tobacco', 'oud', 'patchouli', 'iris', 'vetiver'],
            'reliable': ['cedar', 'sandalwood', 'vetiver', 'oakmoss', 'musk'],
            'low_profile': ['musk', 'soap', 'cotton', 'white_musk', 'aldehydes'],
            'strong_smell': ['oud', 'leather', 'tobacco', 'patchouli', 'ambroxan'],
            'easygoing': ['bergamot', 'musk', 'soap', 'cotton', 'light_floral'],
            'girl_next_door': ['peach', 'apple', 'vanilla', 'freesia', 'lily'],
            'young_lady': ['strawberry', 'peach', 'vanilla', 'cotton_candy', 'peony'],
            'big_brands': ['rose', 'jasmine', 'musk', 'vanilla', 'amber'],
            'well_known': ['lavender', 'rose', 'jasmine', 'vanilla', 'musk'],
            'seen_in_ads': ['coffee', 'vanilla', 'rose', 'jasmine', 'cotton_candy'],
        }

        theme_note_map = {
            'floral': ['rose', 'jasmine', 'peony', 'gardenia', 'tuberose', 'freesia', 'lily', 'orchid', 'champaca', 'ylang', 'iris', 'violet', 'honeysuckle', 'magnolia', 'hyacinth', 'narcissus', 'lilac', 'muguet', 'carnation', 'lotus', 'water_lily', 'bluebell', 'mimosa', 'heliotrope', 'geranium', 'orange_blossom', 'neroli', 'lavender'],
            'floral_fruity': ['rose', 'jasmine', 'peony', 'peach', 'strawberry', 'raspberry', 'lychee', 'bergamot', 'pear', 'apple', 'black_currant', 'freesia', 'lily', 'gardenia'],
            'oriental_floral': ['rose', 'jasmine', 'amber', 'incense', 'vanilla', 'patchouli', 'sandalwood', 'tuberose', 'gardenia', 'orange_blossom'],
            'woody_floral': ['rose', 'jasmine', 'cedar', 'sandalwood', 'violet', 'iris', 'patchouli', 'musk'],
            'woody_fougere': ['cedar', 'sandalwood', 'oakmoss', 'lavender', 'geranium', 'patchouli', 'coumarin'],
            'fougere': ['lavender', 'coumarin', 'oakmoss', 'geranium', 'bergamot'],
            'oriental_woody': ['amber', 'sandalwood', 'cedar', 'incense', 'vanilla', 'oud', 'patchouli'],
            'oriental': ['amber', 'vanilla', 'incense', 'labdanum', 'opoponax', 'myrrh', 'cinnamon', 'clove'],
            'citrus_fougere': ['bergamot', 'lemon', 'grapefruit', 'lavender', 'oakmoss', 'coumarin'],
            'oriental_gourmand': ['vanilla', 'tonka', 'caramel', 'praline', 'chocolate', 'cocoa', 'honey', 'amber', 'cinnamon'],
            'woody_spicy': ['cedar', 'sandalwood', 'pepper', 'cinnamon', 'clove', 'nutmeg', 'cardamom', 'ginger', 'vetiver'],
            'chypre_floral': ['rose', 'jasmine', 'oakmoss', 'patchouli', 'bergamot', 'labdanum'],
            'fruity_gourmand': ['peach', 'strawberry', 'raspberry', 'vanilla', 'caramel', 'tonka', 'praline', 'cocoa'],
            'floral_green': ['rose', 'jasmine', 'galbanum', 'green', 'violet_leaf', 'hyacinth', 'narcissus', 'stem'],
            'oriental_spicy': ['amber', 'incense', 'cinnamon', 'clove', 'nutmeg', 'pepper', 'saffron', 'cardamom', 'vanilla'],
            'spicy_fougere': ['lavender', 'geranium', 'oakmoss', 'pepper', 'cinnamon', 'clove', 'cardamom'],
            'citrus': ['bergamot', 'lemon', 'grapefruit', 'orange', 'mandarin', 'lime', 'yuzu', 'tangerine'],
            'woody': ['cedar', 'sandalwood', 'pine', 'cypress', 'juniper', 'cashmeran', 'akigalawood', 'guaiac_wood'],
            'leather_theme': ['leather', 'suede', 'isobutyl_quinoline', 'birch_tar', 'styrax', 'leather_theme'],
            'fruity_fougere': ['lavender', 'geranium', 'oakmoss', 'peach', 'raspberry', 'apple', 'black_currant'],
            'oriental_fougere': ['lavender', 'geranium', 'oakmoss', 'amber', 'vanilla', 'incense', 'labdanum'],
            'floral_aquatic': ['rose', 'jasmine', 'lily', 'sea', 'aqua', 'marine', 'ozone', 'calone', 'water', 'lotus', 'water_lily'],
            'aquatic_fougere': ['lavender', 'oakmoss', 'geranium', 'sea', 'aqua', 'marine', 'calone', 'coumarin'],
            'chypre': ['bergamot', 'oakmoss', 'patchouli', 'labdanum', 'cistus', 'opoponax'],
            'green_fougere': ['lavender', 'geranium', 'oakmoss', 'green', 'galbanum', 'violet_leaf', 'stem', 'coumarin'],
            'floral_aldehyde': ['rose', 'jasmine', 'lily', 'muguet', 'aldehyde', 'aldehydic', 'sparkling', 'orange_blossom', 'neroli'],
            'chypre_woody': ['bergamot', 'oakmoss', 'patchouli', 'cedar', 'sandalwood', 'labdanum', 'vetiver'],
            'chypre_fruity': ['bergamot', 'oakmoss', 'patchouli', 'labdanum', 'peach', 'raspberry', 'black_currant', 'strawberry'],
            'aquatic_woody': ['cedar', 'sandalwood', 'sea', 'aqua', 'marine', 'ozone', 'calone', 'pine', 'cypress'],
            'citrus_gourmand': ['bergamot', 'lemon', 'orange', 'vanilla', 'tonka', 'caramel', 'praline', 'cocoa'],
        }

        user_notes = set()
        for n in selected_notes:
            user_notes.add(n.lower().replace(' ', '_'))
        for kw in selected_keywords:
            if kw in keyword_note_map:
                user_notes.update(keyword_note_map[kw])
        for th in selected_themes:
            if th in theme_note_map:
                user_notes.update(theme_note_map[th])

        from perfume_engine import PERFUME_DATABASE

        scored = []
        for p in PERFUME_DATABASE:
            if gender != 'unisex' and p.get('gender', 'unisex') not in (gender, 'unisex'):
                continue
            p_notes = set()
            for key in ('notes_top', 'notes_middle', 'notes_base'):
                vals = p.get(key, [])
                if isinstance(vals, list):
                    p_notes.update(v.lower().replace(' ', '_') for v in vals)
                elif isinstance(vals, str):
                    p_notes.update(v.strip().lower().replace(' ', '_') for v in vals.split(',') if v.strip())
            intersection = user_notes & p_notes if user_notes else set()
            union = user_notes | p_notes if user_notes else p_notes
            score = len(intersection) / len(union) if union else 0
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [p for s, p in scored if s > 0][:12]
        if len(top) < 6:
            for s, p in scored:
                if p not in top:
                    top.append(p)
                if len(top) >= 12:
                    break

        total = sum(s for s, _ in scored) if scored else 0
        profile_type = "Dengeli Profil"
        if selected_notes:
            profile_type = "Seçici Nota Profili"
        if selected_themes and not selected_notes:
            profile_type = "Tema Odaklı Profil"

        def clean_perfume(p, score=0):
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
                'image_url': p.get('image_url', ''),
                'benzerlik_yuzde': round(score * 100, 1)
            }

        recs_by_season = {'yaz': [], 'kis': [], 'd\u00f6rt_mevsim': []}
        seen = set()
        for s, p in scored:
            name = p['name']
            if name in seen:
                continue
            season = p.get('season', 'd\u00f6rt_mevsim')
            key = 'd\u00f6rt_mevsim' if season == 'd\u00f6rt_mevsim' else season
            if len(recs_by_season[key]) < 3:
                recs_by_season[key].append(clean_perfume(p, s))
                seen.add(name)
            if all(len(v) >= 3 for v in recs_by_season.values()):
                break

        recommendations = {
            'yaz': recs_by_season['yaz'],
            'kis': recs_by_season['kis'],
            'd\u00f6rt_mevsim': recs_by_season['d\u00f6rt_mevsim'],
            'profile_type': profile_type
        }

        ai_explanations = {}
        try:
            note_profile = {
                'top_pct': 33, 'middle_pct': 33, 'base_pct': 34,
                'top_dominant': 'citrus', 'middle_dominant': 'floral',
                'base_dominant': 'musk', 'profile_type': profile_type,
                'nota_detay': {}
            }
            ai_explanations = generate_explanations(note_profile, recommendations, gender, name)
        except Exception as e:
            print(f"[AI] A\u00e7\u0131klama \u00fcretilemedi: {e}")

        note_profile = {
            'top_pct': round(len(selected_notes) * 8.33) if selected_notes else 33,
            'middle_pct': round(len(selected_keywords) * 8.33) if selected_keywords else 33,
            'base_pct': round(len(selected_themes) * 8.33) if selected_themes else 34,
            'top_dominant': selected_notes[0] if selected_notes else 'citrus',
            'middle_dominant': 'floral',
            'base_dominant': 'musk',
            'profile_type': profile_type,
            'nota_detay': {}
        }

        return jsonify({
            'success': True,
            'gender': gender,
            'note_profile': note_profile,
            'recommendations': recommendations,
            'ai_explanations': ai_explanations,
            'selected_notes': len(selected_notes),
            'selected_keywords': len(selected_keywords),
            'selected_themes': len(selected_themes)
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
@csrf_required
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
