# ParfumAI — Kişisel Koku Analizi
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.
#
# Bu dosya ParfumAI yazılımının bir parçasıdır.
# İzinsiz kopyalanması, dağıtılması veya kullanılması yasaktır.
# Detaylı bilgi için LICENSE dosyasına bakınız.

import json
import os
import uuid
import hashlib
import secrets
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

load_dotenv()

from questions import QUESTIONS, get_regular_questions, get_gender_question
from scoring import ScoringEngine
from perfume_engine import PerfumeMatchingEngine
from ai_service import generate_explanations

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PERMANENT=False
)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = 'admin123'
    print(f"[BILGI] ADMIN_PASSWORD ortam değişkeni ayarlanmamış, varsayılan: admin123")
    print(f"[BILGI] Kalıcı şifre için: set ADMIN_PASSWORD=sifreniz")

FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def csrf_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('_csrf_token') or (request.get_json(silent=True) or {}).get('_csrf_token')
            if not token or token != session.get('_csrf_token'):
                return jsonify({'success': False, 'error': 'CSRF token geçersiz'}), 403
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

matching_engine = PerfumeMatchingEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    gender_q = get_gender_question()
    regular_qs = get_regular_questions()
    return render_template('survey.html', gender_question=gender_q, questions=regular_qs, csrf_token=generate_csrf_token())

@app.route('/api/submit', methods=['POST'])
@csrf_required
def submit_survey():
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        gender_raw = data.get('gender', 'unisex')
        gender = 'unisex'
        normalized = gender_raw.lower().strip()
        if normalized in ['kadin', 'kadın', 'female', 'woman']:
            gender = 'kadın'
        elif normalized in ['erkek', 'male', 'man']:
            gender = 'erkek'
        name = data.get('name', 'Misafir')

        note_profile = ScoringEngine().process_answers(answers)
        recommendations = matching_engine.find_matches(note_profile, gender)

        ai_explanations = {}
        try:
            ai_explanations = generate_explanations(note_profile, recommendations, gender, name)
        except Exception as e:
            print(f"[AI] Açıklama üretilemedi: {e}")

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
                'in_stock': p.get('in_stock', True)
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
                'dört_mevsim': [clean_perfume(p) for p in recommendations['dört_mevsim'][:3]],
                'profile_type': recommendations['profile_type']
            },
            'ai_explanations': ai_explanations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/results')
def results():
    return render_template('results.html', csrf_token=generate_csrf_token())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/questions')
def get_questions():
    gender_q = get_gender_question()
    regular_qs = get_regular_questions()
    return jsonify({"gender": gender_q, "regular": regular_qs})

@app.route('/api/node_categories')
def get_note_categories():
    from scoring import NOTE_CATEGORIES
    return jsonify(NOTE_CATEGORIES)

@app.route('/api/stock')
def get_stock():
    from perfume_engine import PERFUME_DATABASE
    stock = {}
    for p in PERFUME_DATABASE:
        stock[p['name']] = {
            'in_stock': p.get('in_stock', True),
            'price_range': p.get('price_range', '')
        }
    return jsonify(stock)

@app.route('/api/explain', methods=['POST'])
def api_explain():
    try:
        data = request.get_json()
        print(f"[AI] /api/explain data type: {type(data).__name__}")
        if isinstance(data, dict):
            print(f"[AI] note_profile type: {type(data.get('note_profile')).__name__}")
        perfumes = data.get('perfumes', []) if isinstance(data, dict) else []
        note_profile = data.get('note_profile', {}) if isinstance(data, dict) else data
        if isinstance(note_profile, str):
            import json as _json
            try: note_profile = _json.loads(note_profile)
            except: note_profile = {}
        gender = data.get('gender', 'unisex') if isinstance(data, dict) else 'unisex'
        name = data.get('name', 'Misafir') if isinstance(data, dict) else 'Misafir'

        recommendations = matching_engine.find_matches(note_profile, gender)
        explanations = generate_explanations(note_profile, recommendations, gender, name)

        # Sadece istenen parfümlerin açıklamalarını filtrele
        result = {}
        for p in perfumes:
            if p in explanations:
                result[p] = explanations[p]

        return jsonify({'success': True, 'explanations': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/log-sale', methods=['POST'])
@csrf_required
def log_sale():
    try:
        data = request.get_json()
        import csv
        import os
        log_path = os.path.join(os.path.dirname(__file__), 'data', 'sales_log.csv')
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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        token = request.form.get('_csrf_token')
        if not token or token != session.get('_csrf_token'):
            return render_template('admin_login.html', error='CSRF token geçersiz!', csrf_token=generate_csrf_token())
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_stats'))
        return render_template('admin_login.html', error='Hatalı şifre!', csrf_token=generate_csrf_token())
    return render_template('admin_login.html', error=None, csrf_token=generate_csrf_token())

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/perfumes')
@login_required
def admin_perfumes():
    from perfume_engine import _init_database, save_database
    perfumes = _init_database()
    search = request.args.get('q', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 50

    if search:
        perfumes = [p for p in perfumes if search in p['name'].lower() or search in p['brand'].lower()]

    total = len(perfumes)
    pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    page_perfumes = perfumes[start:end]

    return render_template('admin_perfumes.html',
                          perfumes=page_perfumes,
                          search=search,
                          page=page,
                          pages=pages,
                          total=total,
                          csrf_token=generate_csrf_token())

@app.route('/admin/perfumes/toggle-stock', methods=['POST'])
@login_required
@csrf_required
def toggle_stock():
    from perfume_engine import _init_database, save_database, _write_audit, check_critical_stock
    data = request.get_json()
    name = data.get('name', '')
    perfumes = _init_database()
    for p in perfumes:
        if p['name'] == name:
            old_val = p.get('in_stock', True)
            p['in_stock'] = not old_val
            save_database()
            _write_audit("admin", "TOGGLE_STOCK", "perfume_database",
                        perfumes.index(p), {"in_stock": old_val}, {"in_stock": p['in_stock']})
            check_critical_stock(name, old_val, p['in_stock'])
            return jsonify({'success': True, 'in_stock': p['in_stock']})
    return jsonify({'success': False, 'error': 'Parfüm bulunamadı'}), 404

@app.route('/admin/perfumes/edit', methods=['POST'])
@login_required
@csrf_required
def edit_perfume():
    from perfume_engine import _init_database, save_database, _write_audit, check_critical_stock
    data = request.get_json()
    name = data.get('name', '')
    field = data.get('field', '')
    value = data.get('value', '')
    perfumes = _init_database()
    for p in perfumes:
        if p['name'] == name and field in p:
            old_val = p[field]
            if field in ('in_stock',):
                p[field] = bool(value)
            elif field in ('price_range', 'description'):
                p[field] = str(value) if value else p[field]
            save_database()
            _write_audit("admin", "EDIT", "perfume_database",
                        perfumes.index(p), {field: old_val}, {field: p[field]})
            if field == "in_stock":
                check_critical_stock(name, old_val, p['in_stock'])
            return jsonify({'success': True, 'value': p[field]})
    return jsonify({'success': False, 'error': 'Parfüm veya alan bulunamadı'}), 404

@app.route('/admin/perfumes/add', methods=['POST'])
@login_required
@csrf_required
def add_perfume():
    from perfume_engine import _init_database, save_database, _write_audit
    data = request.get_json()
    required = ['name', 'brand', 'season', 'gender', 'price_range', 'description']
    for field in required:
        if not data.get(field, '').strip():
            return jsonify({'success': False, 'error': f'{field} zorunlu'}), 400
    perfumes = _init_database()
    for p in perfumes:
        if p['name'].lower() == data['name'].strip().lower():
            return jsonify({'success': False, 'error': 'Bu isimde parfüm zaten var'}), 400
    new_p = {
        "name": data['name'].strip(),
        "brand": data['brand'].strip(),
        "season": data['season'].strip(),
        "gender": data['gender'].strip(),
        "price_range": data['price_range'].strip(),
        "description": data['description'].strip(),
        "notes_top": data.get('notes_top', '').split(','),
        "notes_middle": data.get('notes_middle', '').split(','),
        "notes_base": data.get('notes_base', '').split(','),
        "profile": {"top_pct": 33, "middle_pct": 33, "base_pct": 34},
        "in_stock": True
    }
    for key in ('notes_top', 'notes_middle', 'notes_base'):
        new_p[key] = [n.strip().lower().replace(' ', '_') for n in new_p[key] if n.strip()]
    from perfume_engine import PERFUME_DATABASE
    PERFUME_DATABASE.append(new_p)
    save_database()
    _write_audit("admin", "ADD", "perfume_database", len(PERFUME_DATABASE)-1, None, new_p)
    return jsonify({'success': True, 'perfume': new_p})

@app.route('/admin/perfumes/delete', methods=['POST'])
@login_required
@csrf_required
def delete_perfume():
    from perfume_engine import _init_database, save_database, _write_audit
    data = request.get_json()
    name = data.get('name', '')
    perfumes = _init_database()
    for i, p in enumerate(perfumes):
        if p['name'] == name:
            removed = perfumes.pop(i)
            from perfume_engine import PERFUME_DATABASE
            PERFUME_DATABASE[:] = perfumes
            save_database()
            _write_audit("admin", "DELETE", "perfume_database", i, removed, None)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Parfüm bulunamadı'}), 404

@app.route('/admin')
@login_required
def admin_stats():
    import csv
    import os
    log_path = os.path.join(os.path.dirname(__file__), 'data', 'sales_log.csv')
    sales = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sales = list(reader)

    from perfume_engine import _init_database
    perfumes = _init_database()
    total_perfumes = len(perfumes)
    in_stock = sum(1 for p in perfumes if p.get('in_stock', True))

    return render_template('admin.html',
                          sales=sales,
                          total_sales=len(sales),
                          total_perfumes=total_perfumes,
                          in_stock=in_stock)

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='127.0.0.1', port=5000)
