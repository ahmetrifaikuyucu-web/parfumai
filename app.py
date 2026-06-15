# ParfumAI — Ki\u015fisel Koku Analizi
# Copyright (c) 2026 Ahmet R\u0131fai Kuyucu
# T\u00fcm Haklar\u0131 Sakl\u0131d\u0131r — All Rights Reserved.
#
# Bu dosya ParfumAI yaz\u0131l\u0131m\u0131n\u0131n bir par\u00e7as\u0131d\u0131r.
# \u0130zinsiz kopyalanmas\u0131, da\u011f\u0131t\u0131lmas\u0131 veya kullan\u0131lmas\u0131 yasakt\u0131r.
# Detayl\u0131 bilgi i\u00e7in LICENSE dosyas\u0131na bak\u0131n\u0131z.

import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from whitenoise import WhiteNoise

load_dotenv()

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable is required. Set it before running the application.")

FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

def precompute_similarity():
    try:
        from perfume_engine import PERFUME_DATABASE
        from ml_similarity import precompute_similarity as pcs
        matrix, vec, ids = pcs(PERFUME_DATABASE)
        print(f"[ML] Benzerlik matrisi hazır: {len(ids)} parfüm")
    except Exception as e:
        print(f"[ML] Benzerlik matrisi yüklenemedi: {e}")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_PERMANENT=False,
        CACHE_TYPE='SimpleCache',
        CACHE_DEFAULT_TIMEOUT=300,
        RATELIMIT_DEFAULT='200/day;50/hour',
        RATELIMIT_STORAGE_URL='memory://'
    )

    # Middleware
    CORS(app)
    Cache(app)
    Limiter(get_remote_address, app=app, default_limits=['200 per day', '50 per hour'])
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

    # G\u00fcvenlik header'lar\u0131
    @app.after_request
    def add_security_headers(response):
        if not request.path.startswith('/admin') and not request.path.startswith('/api'):
            response.headers['Cache-Control'] = 'public, max-age=86400'
        else:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Blueprint'leri kaydet
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # ML benzerlik matrisini ön hesapla
    with app.app_context():
        precompute_similarity()

    return app

app = create_app()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(debug=FLASK_DEBUG, host='127.0.0.1', port=port)
