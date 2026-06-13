# ParfumAI — Paylaşılan Yardımcı Fonksiyonlar
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

import secrets
from functools import wraps
from flask import session, request, jsonify, redirect, url_for

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
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated
