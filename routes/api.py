from flask import Blueprint, request, jsonify
from utils import csrf_required
from legacy.scoring import ScoringEngine, NOTE_CATEGORIES
from perfume_engine import matching_engine
from ai_service import generate_explanations
import json
import os

api_bp = Blueprint('api', __name__)

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
    'floral': ['rose', 'jasmine', 'peony', 'gardenia', 'tuberose', 'freesia', 'lily', 'orchid', 'champaca', 'ylang', 'iris', 'violet', 'honeysuckle', 'magnolia', 'hyacinth', 'narcissus', 'lilac', 'muguet', 'carnation', 'lotus', 'water_lily', 'bluebell', 'mimosa', 'heliotrope', 'geranium', 'orange_blossom', 'neroli', 'lavender'],  # noqa: E501
    'floral_fruity': ['rose', 'jasmine', 'peony', 'peach', 'strawberry', 'raspberry', 'lychee', 'bergamot', 'pear', 'apple', 'black_currant', 'freesia', 'lily', 'gardenia'],  # noqa: E501
    'oriental_floral': ['rose', 'jasmine', 'amber', 'incense', 'vanilla', 'patchouli', 'sandalwood', 'tuberose', 'gardenia', 'orange_blossom'],  # noqa: E501
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
    'floral_aquatic': ['rose', 'jasmine', 'lily', 'sea', 'aqua', 'marine', 'ozone', 'calone', 'water', 'lotus', 'water_lily'],  # noqa: E501
    'aquatic_fougere': ['lavender', 'oakmoss', 'geranium', 'sea', 'aqua', 'marine', 'calone', 'coumarin'],
    'chypre': ['bergamot', 'oakmoss', 'patchouli', 'labdanum', 'cistus', 'opoponax'],
    'green_fougere': ['lavender', 'geranium', 'oakmoss', 'green', 'galbanum', 'violet_leaf', 'stem', 'coumarin'],
    'floral_aldehyde': ['rose', 'jasmine', 'lily', 'muguet', 'aldehyde', 'aldehydic', 'sparkling', 'orange_blossom', 'neroli'],  # noqa: E501
    'chypre_woody': ['bergamot', 'oakmoss', 'patchouli', 'cedar', 'sandalwood', 'labdanum', 'vetiver'],
    'chypre_fruity': ['bergamot', 'oakmoss', 'patchouli', 'labdanum', 'peach', 'raspberry', 'black_currant', 'strawberry'],  # noqa: E501
    'aquatic_woody': ['cedar', 'sandalwood', 'sea', 'aqua', 'marine', 'ozone', 'calone', 'pine', 'cypress'],
    'citrus_gourmand': ['bergamot', 'lemon', 'orange', 'vanilla', 'tonka', 'caramel', 'praline', 'cocoa'],
}


def _clean_perfume(p, score=0):
    return {
        'name': p.get('name', ''),
        'brand': p.get('brand', ''),
        'season': p.get('season', 'dört_mevsim'),
        'gender': p.get('gender', 'unisex'),
        'description': p.get('description', ''),
        'price_range': p.get('price_range', ''),
        'notes_top': p.get('notes_top', []),
        'notes_middle': p.get('notes_middle', []),
        'notes_base': p.get('notes_base', []),
        'in_stock': p.get('in_stock', True),
        'image_url': p.get('image_url', ''),
        'benzerlik_yuzde': round(score * 100, 1) if score else p.get('benzerlik_yuzde', 0)
    }


@api_bp.route('/api/submit', methods=['POST'])
@csrf_required
def submit_survey():  # noqa: C901
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

        note_layer_counts = {}
        top_db_set = set()
        middle_db_set = set()
        base_db_set = set()
        for p in PERFUME_DATABASE:
            for key, layer in [('notes_top', 'top'), ('notes_middle', 'middle'), ('notes_base', 'base')]:
                vals = p.get(key, [])
                if isinstance(vals, list):
                    for v in vals:
                        v_norm = v.lower().replace(' ', '_')
                        if layer == 'top':
                            top_db_set.add(v_norm)
                        elif layer == 'middle':
                            middle_db_set.add(v_norm)
                        else:
                            base_db_set.add(v_norm)
                        if v_norm in user_notes:
                            if v_norm not in note_layer_counts:
                                note_layer_counts[v_norm] = {'top': 0, 'middle': 0, 'base': 0}
                            note_layer_counts[v_norm][layer] += 1

        top_total = sum(c['top'] for c in note_layer_counts.values())
        middle_total = sum(c['middle'] for c in note_layer_counts.values())
        base_total = sum(c['base'] for c in note_layer_counts.values())
        total = top_total + middle_total + base_total
        if total == 0:
            top_pct, middle_pct, base_pct = 33, 33, 34
        else:
            top_pct = round((top_total / total) * 100)
            middle_pct = round((middle_total / total) * 100)
            base_pct = 100 - top_pct - middle_pct

        top_dominant = next((n for n in selected_notes if n.lower().replace(' ', '_') in top_db_set), None)
        middle_dominant = next((n for n in selected_notes if n.lower().replace(' ', '_') in middle_db_set), None)
        base_dominant = next((n for n in selected_notes if n.lower().replace(' ', '_') in base_db_set), None)

        note_profile = {
            'top_pct': top_pct,
            'middle_pct': middle_pct,
            'base_pct': base_pct,
            'top_dominant': top_dominant or ('citrus' if selected_notes else 'citrus'),
            'middle_dominant': middle_dominant or 'floral',
            'base_dominant': base_dominant or 'musk',
            'profile_type': 'Kullan\u0131c\u0131 Profili',
            'nota_detay': {}
        }

        raw_recs = matching_engine.find_matches(note_profile, gender)

        recommendations = {
            'yaz': [_clean_perfume(p) for p in raw_recs.get('yaz', [])],
            'kis': [_clean_perfume(p) for p in raw_recs.get('kis', [])],
            'd\u00f6rt_mevsim': [_clean_perfume(p) for p in raw_recs.get('d\u00f6rt_mevsim', [])],
            'profile_type': raw_recs.get('profile_type', 'Kullan\u0131c\u0131 Profili')
        }
        note_profile['profile_type'] = recommendations['profile_type']

        ai_explanations = {}
        try:
            ai_explanations = generate_explanations(note_profile, recommendations, gender, name)
        except Exception as e:
            print(f"[AI] A\u00e7\u0131klama \u00fcretilemedi: {e}")

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
    except Exception:
        return jsonify({'success': False, 'error': 'İşlem sırasında bir hata oluştu'}), 400


@api_bp.route('/api/submit-simple', methods=['POST'])
@csrf_required
def submit_simple():
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
        answers = data.get('answers', {})

        engine = ScoringEngine()
        note_profile = engine.process_answers(answers)

        raw_recs = matching_engine.find_matches(note_profile, gender)

        recommendations = {
            'yaz': [_clean_perfume(p) for p in raw_recs.get('yaz', [])],
            'kis': [_clean_perfume(p) for p in raw_recs.get('kis', [])],
            'd\u00f6rt_mevsim': [_clean_perfume(p) for p in raw_recs.get('d\u00f6rt_mevsim', [])],
            'profile_type': raw_recs.get('profile_type', note_profile.get('profile_type', 'Kullan\u0131c\u0131 Profili'))  # noqa: E501
        }
        note_profile['profile_type'] = recommendations['profile_type']

        ai_explanations = {}
        try:
            ai_explanations = generate_explanations(note_profile, recommendations, gender, name)
        except Exception as e:
            print(f"[AI] A\u00e7\u0131klama \u00fcretilemedi: {e}")

        return jsonify({
            'success': True,
            'gender': gender,
            'note_profile': note_profile,
            'recommendations': recommendations,
            'ai_explanations': ai_explanations
        })
    except Exception:
        return jsonify({'success': False, 'error': 'Cevap işlenirken bir hata oluştu'}), 400


@api_bp.route('/api/questions')
def get_questions():
    from legacy.questions import get_gender_question, get_regular_questions
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
            try:
                note_profile = json.loads(note_profile)
            except Exception:
                note_profile = {}
        gender = data.get('gender', 'unisex') if isinstance(data, dict) else 'unisex'
        name = data.get('name', 'Misafir') if isinstance(data, dict) else 'Misafir'

        recommendations = matching_engine.find_matches(note_profile, gender)
        explanations = generate_explanations(note_profile, recommendations, gender, name)

        result = {}
        for p in perfumes:
            if p in explanations:
                result[p] = explanations[p]

        return jsonify({'success': True, 'explanations': result})
    except Exception:
        return jsonify({'success': False, 'error': 'Açıklama alınamadı'}), 400


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
    except Exception:
        return jsonify({'success': False, 'error': 'Satış kaydedilemedi'}), 400


@api_bp.route('/api/similar/<path:name>')
def get_similar(name):
    from urllib.parse import unquote
    from perfume_engine import PERFUME_DATABASE
    from ml_similarity import find_similar

    decoded = unquote(name)
    source = next((p for p in PERFUME_DATABASE if p['name'] == decoded), None)
    if not source:
        return jsonify({'success': False, 'error': 'Parfüm bulunamadı'}), 404

    similar = find_similar(decoded, PERFUME_DATABASE, top_n=9)
    if not similar:
        similar = [dict(p) for p in PERFUME_DATABASE[:9]]

    for p in similar:
        if p['name'] == decoded and 'benzerlik_yuzde' in p:
            del p['benzerlik_yuzde']

    return jsonify({
        'success': True,
        'source': _clean_perfume(source),
        'similar': [_clean_perfume(p) for p in similar]
    })
