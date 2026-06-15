import os
import json
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils import generate_csrf_token, csrf_required, login_required
from perfume_engine import _init_database, save_database, PERFUME_DATABASE, _write_audit, check_critical_stock
from ml_similarity import clear_cache as clear_ml_cache

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        token = request.form.get('_csrf_token')
        if not token or token != session.get('_csrf_token'):
            return render_template('admin_login.html', error='CSRF token ge\u00e7ersiz!', csrf_token=generate_csrf_token())
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_stats'))
        return render_template('admin_login.html', error='Hatal\u0131 \u015fifre!', csrf_token=generate_csrf_token())
    return render_template('admin_login.html', error=None, csrf_token=generate_csrf_token())


@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))


@admin_bp.route('/admin/perfumes')
@login_required
def admin_perfumes():
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


@admin_bp.route('/admin/perfumes/toggle-stock', methods=['POST'])
@login_required
@csrf_required
def toggle_stock():
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
    return jsonify({'success': False, 'error': 'Parf\u00fcm bulunamad\u0131'}), 404


@admin_bp.route('/admin/perfumes/edit', methods=['POST'])
@login_required
@csrf_required
def edit_perfume():
    data = request.get_json()
    name = data.get('name', '')
    field = data.get('field', '')
    value = data.get('value', '')
    perfumes = _init_database()
    for p in perfumes:
        if p['name'] == name and field in p:
            old_val = p[field]
            if field in ('in_stock',):
                p[field] = str(value).lower() in ('true', '1')
            elif field in ('price_range', 'description', 'season', 'gender'):
                p[field] = str(value) if value else p[field]
            elif field in ('notes_top', 'notes_middle', 'notes_base'):
                raw = str(value) if value else ''
                p[field] = [n.strip().lower().replace(' ', '_') for n in raw.split(',') if n.strip()]
            save_database()
            _write_audit("admin", "EDIT", "perfume_database",
                        perfumes.index(p), {field: old_val}, {field: p[field]})
            if field == "in_stock":
                check_critical_stock(name, old_val, p['in_stock'])
            return jsonify({'success': True, 'value': p[field]})
    return jsonify({'success': False, 'error': 'Parf\u00fcm veya alan bulunamad\u0131'}), 404


@admin_bp.route('/admin/perfumes/add', methods=['POST'])
@login_required
@csrf_required
def add_perfume():
    data = request.get_json()
    required = ['name', 'brand', 'season', 'gender', 'price_range', 'description']
    for field in required:
        if not data.get(field, '').strip():
            return jsonify({'success': False, 'error': f'{field} zorunlu'}), 400
    perfumes = _init_database()
    for p in perfumes:
        if p['name'].lower() == data['name'].strip().lower():
            return jsonify({'success': False, 'error': 'Bu isimde parf\u00fcm zaten var'}), 400
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
    PERFUME_DATABASE.append(new_p)
    save_database()
    clear_ml_cache()
    _write_audit("admin", "ADD", "perfume_database", len(PERFUME_DATABASE)-1, None, new_p)
    return jsonify({'success': True, 'perfume': new_p})


@admin_bp.route('/admin/perfumes/delete', methods=['POST'])
@login_required
@csrf_required
def delete_perfume():
    data = request.get_json()
    name = data.get('name', '')
    perfumes = _init_database()
    for i, p in enumerate(perfumes):
        if p['name'] == name:
            removed = perfumes.pop(i)
            PERFUME_DATABASE[:] = perfumes
            save_database()
            clear_ml_cache()
            _write_audit("admin", "DELETE", "perfume_database", i, removed, None)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Parf\u00fcm bulunamad\u0131'}), 404


@admin_bp.route('/admin')
@login_required
def admin_stats():
    import csv
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sales_log.csv')
    sales = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sales = list(reader)

    perfumes = _init_database()
    total_perfumes = len(perfumes)
    in_stock = sum(1 for p in perfumes if p.get('in_stock', True))

    return render_template('admin.html',
                          sales=sales,
                          total_sales=len(sales),
                          total_perfumes=total_perfumes,
                          in_stock=in_stock)


@admin_bp.route('/api/admin/audit-log')
@login_required
def audit_log():
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'audit_log.jsonl')
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return jsonify({'logs': logs[-50:]})
