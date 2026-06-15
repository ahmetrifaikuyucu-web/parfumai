# ParfumAI — API Testleri
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

import json
import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: E402


def _csrf(client):
    r = client.get('/survey')
    m = re.search(r"CSRF_TOKEN\s*=\s*'([^']+)'", r.data.decode())
    return m.group(1) if m else ''


def test_index_returns_200():
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200


def test_survey_returns_200():
    with app.test_client() as client:
        resp = client.get('/survey')
        assert resp.status_code == 200


def test_about_returns_200():
    with app.test_client() as client:
        resp = client.get('/about')
        assert resp.status_code == 200


def test_results_returns_200():
    with app.test_client() as client:
        resp = client.get('/results')
        assert resp.status_code == 200


def test_api_questions_returns_json():
    with app.test_client() as client:
        resp = client.get('/api/questions')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert 'gender' in data
        assert 'regular' in data


def test_api_submit_valid():
    with app.test_client() as client:
        token = _csrf(client)
        resp = client.post('/api/submit', json={
            'answers': {1: 0, 4: 1, 6: 2, 7: 3, 11: 1, 12: 2},
            'gender': 'kadin',
            'name': 'Test',
            '_csrf_token': token
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success']
        assert 'note_profile' in data
        assert 'recommendations' in data


def test_api_submit_invalid_gender_defaults():
    with app.test_client() as client:
        token = _csrf(client)
        resp = client.post('/api/submit', json={
            'answers': {1: 0, 4: 1, 6: 2, 7: 3, 11: 1, 12: 2},
            'gender': 'unknown_value',
            'name': 'Test',
            '_csrf_token': token
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success']


def test_api_submit_empty_answers_still_works():
    with app.test_client() as client:
        token = _csrf(client)
        resp = client.post('/api/submit', json={
            'answers': {},
            'gender': 'erkek',
            'name': 'Test',
            '_csrf_token': token
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success']


def test_api_stock_returns_all():
    with app.test_client() as client:
        resp = client.get('/api/stock')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) > 300


def test_admin_redirects_when_not_logged_in():
    with app.test_client() as client:
        resp = client.get('/admin')
        assert resp.status_code == 302


def test_admin_login_valid():
    import os
    import importlib
    import app as app_module
    original = os.environ.get('ADMIN_PASSWORD')
    os.environ['ADMIN_PASSWORD'] = 'test123'
    importlib.reload(app_module)
    with app_module.app.test_client() as client:
        login_page = client.get('/admin/login')
        csrf_match = re.search(r'name="_csrf_token" value="([^"]+)"', login_page.data.decode())
        csrf_token = csrf_match.group(1) if csrf_match else ''
        resp = client.post('/admin/login', data={'password': 'test123', '_csrf_token': csrf_token})
        assert resp.status_code == 302
        resp2 = client.get('/admin')
        assert resp2.status_code == 200
    if original:
        os.environ['ADMIN_PASSWORD'] = original


if __name__ == '__main__':
    test_index_returns_200()
    test_survey_returns_200()
    test_about_returns_200()
    test_api_questions_returns_json()
    test_api_submit_valid()
    test_api_submit_invalid_gender_defaults()
    test_api_submit_empty_answers_still_works()
    test_api_stock_returns_all()
    test_admin_redirects_when_not_logged_in()
    test_admin_login_valid()
    print(f"All {10} API tests passed!")
