import hashlib
import json
import os
import time
import requests
from bs4 import BeautifulSoup

CACHE_DIR = None

def _get_cache_dir():
    global CACHE_DIR
    if CACHE_DIR is None:
        CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
    os.makedirs(CACHE_DIR, exist_ok=True)
    return CACHE_DIR

def search_fragrantica(query, max_results=5):
    cache_dir = _get_cache_dir()
    cache_key = hashlib.md5(f"fragrantica_{query}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 86400:
        with open(cache_path, "r") as f:
            return json.load(f)

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        url = f"https://www.fragrantica.com/search/?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        items = soup.select(".grid-item a, .search-result-item, .perfume-card")[:max_results]
        for item in items:
            name = item.get_text(strip=True)
            link = item.get("href", "")
            if name and link:
                results.append({"name": name, "url": f"https://www.fragrantica.com{link}" if link.startswith("/") else link})
        with open(cache_path, "w") as f:
            json.dump(results, f)
        return results
    except Exception:
        import traceback
        traceback.print_exc()
        return []


def search_parfumo(query, max_results=5):
    cache_dir = _get_cache_dir()
    cache_key = hashlib.md5(f"parf%C3%BCmo_{query}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 86400:
        with open(cache_path, "r") as f:
            return json.load(f)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        url = f"https://www.parf%C3%BCmo.com/search?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        items = soup.select(".perfume-card, .search-item, a[href*='perfume']")[:max_results]
        seen = set()
        for item in items:
            href = item.get("href", "")
            text = item.get_text(strip=True)
            if href and text and "perfume" in href.lower():
                full_url = f"https://www.parf%C3%BCmo.com{href}" if href.startswith("/") else href
                if text not in seen:
                    seen.add(text)
                    results.append({"name": text, "url": full_url})
        with open(cache_path, "w") as f:
            json.dump(results, f)
        return results
    except Exception:
        import traceback
        traceback.print_exc()
        return []
