# ParfumAI — Fragrantica Scraper
# Copyright (c) 2026 Ahmet Rıfai Kuyucu

import time
import json
import os
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SCRAPED_PATH = os.path.join(DATA_DIR, 'fragrantica_scraped.json')


def scrape_perfume(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return {'error': f'Fragrantica bağlantı hatası'}

    soup = BeautifulSoup(resp.text, 'html.parser')
    result = {'url': url, 'name': '', 'brand': '', 'notes_top': [], 'notes_middle': [], 'notes_base': []}

    title_el = soup.select_one('h1[itemprop="name"], .perfume-title, h1')
    if title_el:
        result['name'] = title_el.get_text(strip=True)

    brand_el = soup.select_one('a[itemprop="brand"], .brand-link, .designer-link')
    if brand_el:
        result['brand'] = brand_el.get_text(strip=True)

    note_sections = soup.select('.notes-box, .pyramid-notes, .note-box')
    for section in note_sections:
        section_text = section.get_text(separator=' ', strip=True).lower()
        notes = [n.strip() for n in re.split(r'[,;]', section_text) if n.strip()]

        header = section.find_previous(['h3', 'h4', 'strong'])
        header_text = header.get_text(strip=True).lower() if header else ''

        if 'top' in header_text or 'head' in header_text or 'üst' in header_text:
            result['notes_top'].extend(notes)
        elif 'middle' in header_text or 'heart' in header_text or 'orta' in header_text:
            result['notes_middle'].extend(notes)
        elif 'base' in header_text or 'bottom' in header_text or 'alt' in header_text:
            result['notes_base'].extend(notes)

    return result


def scrape_by_brand(brand_name, max_pages=2):
    results = []
    base_url = f'https://www.fragrantica.com/designers/{brand_name.lower().replace(" ", "-")}.html'

    for page in range(1, max_pages + 1):
        url = f'{base_url}?page={page}' if page > 1 else base_url
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            break

        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for a in soup.select('a[href*="/perfume/"]'):
            href = a.get('href', '')
            if href and '/perfume/' in href and not href.startswith('http'):
                href = 'https://www.fragrantica.com' + href
            if href and href not in links:
                links.append(href)

        for link in links:
            data = scrape_perfume(link)
            if data and data.get('name'):
                results.append(data)
            time.sleep(1.5)

    if results:
        os.makedirs(DATA_DIR, exist_ok=True)
        existing = []
        if os.path.exists(SCRAPED_PATH):
            with open(SCRAPED_PATH, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        all_data = existing + results
        with open(SCRAPED_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"[Scraper] {len(results)} yeni parfüm eklendi. Toplam: {len(all_data)}")

    return results


def merge_into_database():
    if not os.path.exists(SCRAPED_PATH):
        print("[Scraper] Kazınmış veri bulunamadı.")
        return

    with open(SCRAPED_PATH, 'r', encoding='utf-8') as f:
        scraped = json.load(f)

    from perfume_engine import PERFUME_DATABASE, save_database
    existing_names = {p['name'] for p in PERFUME_DATABASE}

    added = 0
    for item in scraped:
        name = item.get('name', '')
        if not name or name in existing_names:
            continue

        top = item.get('notes_top', [])
        middle = item.get('notes_middle', [])
        base = item.get('notes_base', [])
        if not any([top, middle, base]):
            continue

        PERFUME_DATABASE.append({
            'name': name,
            'brand': item.get('brand', 'Bilinmeyen'),
            'notes_top': top[:6],
            'notes_middle': middle[:6],
            'notes_base': base[:6],
            'profile': {'top_pct': 33, 'middle_pct': 33, 'base_pct': 34},
            'season': 'dört_mevsim',
            'gender': 'unisex',
            'description': f"Fragrantica'dan eklendi.",
            'price_range': 'Belirtilmemiş',
            'in_stock': True
        })
        existing_names.add(name)
        added += 1

    if added > 0:
        save_database()
        print(f"[Scraper] {added} parfüm veritabanına eklendi.")
