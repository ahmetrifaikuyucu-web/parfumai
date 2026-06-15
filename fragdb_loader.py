# ParfumAI — FragDB Veritabani Entegrasyon Modulu
# Copyright (c) 2026 Ahmet Rifai Kuyucu
# Tum Haklari Saklidir — All Rights Reserved.
#
# FragDB: 130.000+ parfum, 7.800+ marka, 2.500+ nota
# Kaynak: https://huggingface.co/datasets/FragDBnet/fragrance-database
# Lisans: CC-BY-NC-4.0 (ticari olmayan kullanim icin ucretsiz)
#
# Kullanim:
#   pip install pandas
#   python -c "from fragdb_loader import convert_sample; convert_sample()"

import os
import re
import json
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'fragdb_database.json')
SAMPLE_SIZE = 10  # HuggingFace'deki ornek boyutu

def parse_notes_pyramid(notes_str):
    """FragDB notes_pyramid -> {top: [note_names], middle: [note_names], base: [note_names]}"""
    result = {"top": [], "middle": [], "base": []}
    if not notes_str or not isinstance(notes_str, str):
        return result

    for layer in ['top', 'middle', 'base']:
        pattern = rf'{layer}\((.*?)\)'
        match = re.search(pattern, notes_str)
        if match:
            entries = match.group(1).split(';')
            for entry in entries:
                parts = entry.split(',')
                if len(parts) >= 2:
                    result[layer].append(parts[0].strip())

    return result


def parse_brand(brand_str):
    """FragDB 'Name;bID' -> name"""
    if not brand_str or not isinstance(brand_str, str):
        return ''
    return brand_str.split(';')[0].strip()


def map_gender(gender_str):
    """FragDB gender -> kadin/erkek/unisex"""
    if not gender_str:
        return 'unisex'
    if 'women' in gender_str or 'female' in gender_str:
        return 'kadin'
    elif 'men' in gender_str or 'male' in gender_str:
        return 'erkek'
    return 'unisex'


def parse_season(season_str):
    """FragDB season votes -> yaz/kis/dort_mevsim"""
    if not season_str or not isinstance(season_str, str):
        return 'dort_mevsim'

    scores = {}
    for part in season_str.split(';'):
        if ':' in part:
            key, val = part.split(':')[:2]
            season_key = key.replace('season_', '')
            try:
                scores[season_key] = float(val)
            except ValueError:
                scores[season_key] = 0

    if not scores:
        return 'dort_mevsim'

    # En yuksek oy alan mevsim
    dominant = max(scores, key=scores.get)

    # FragDB kullanimina gore haritalama
    season_map = {
        'winter': 'kis',
        'summer': 'yaz',
        'spring': 'yaz',  # ilkbahar -> yaz kategorisine
        'fall': 'kis'      # sonbahar -> kis kategorisine
    }
    return season_map.get(dominant, 'dort_mevsim')


def clean_html(raw):
    """HTML'den duz metin cikar"""
    if not raw or not isinstance(raw, str):
        return ''
    text = re.sub(r'<[^>]+>', ' ', raw)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:300]  # Ilk 300 karakter


def parse_year(year_val):
    """Parfum yilini sayiya cevir"""
    try:
        y = int(year_val)
        if 1800 <= y <= 2030:
            return y
    except (ValueError, TypeError):
        pass
    return None


def load_fragdb_csv(csv_path):
    """FragDB CSV'sini yukle ve normalize et"""
    import pandas as pd
    df = pd.read_csv(csv_path, sep='|')
    perfumes = []

    for _, row in df.iterrows():
        notes = parse_notes_pyramid(row.get('notes_pyramid', ''))
        brand = parse_brand(row.get('brand', ''))
        gender = map_gender(row.get('gender', ''))
        season = parse_season(row.get('season', ''))
        desc = clean_html(row.get('description', ''))
        year = parse_year(row.get('year', ''))
        name = str(row.get('name', '')).strip()
        pid = row.get('pid', '')

        if not name or not brand:
            continue

        perfume = {
            "name": name,
            "brand": brand,
            "season": season,
            "gender": gender,
            "price_range": "",
            "description": desc,
            "notes_top": notes.get("top", [])[:5],
            "notes_middle": notes.get("middle", [])[:5],
            "notes_base": notes.get("base", [])[:5],
            "profile": {"top_pct": 33, "middle_pct": 33, "base_pct": 34},
            "in_stock": True,
            "fragdb_id": pid,
            "year": year,
            "image_url": row.get('main_photo', '')
        }
        perfumes.append(perfume)

    return perfumes


def convert_fragdb(csv_path=None, output_path=None, max_perfumes=None):
    """FragDB CSV -> JSON donusumu"""
    if csv_path is None:
        # HuggingFace cache'inde ara
        cache_base = os.path.expanduser(
            '~/.cache/huggingface/hub/datasets--FragDBnet--fragrance-database/snapshots'
        )
        if os.path.exists(cache_base):
            snapshots = sorted(os.listdir(cache_base), reverse=True)
            if snapshots:
                csv_path = os.path.join(cache_base, snapshots[0], 'fragrances.csv')

    if not csv_path or not os.path.exists(csv_path):
        print(f"[FRAGDB] CSV bulunamadi: {csv_path}")
        print("  Indirmek icin: pip install huggingface-hub")
        print("  from huggingface_hub import hf_hub_download; hf_hub_download(...)")
        return []

    print(f"[FRAGDB] Yukleniyor: {csv_path}")
    perfumes = load_fragdb_csv(csv_path)

    if max_perfumes and len(perfumes) > max_perfumes:
        perfumes = perfumes[:max_perfumes]

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(perfumes, f, ensure_ascii=False, indent=2)
        print(f"[FRAGDB] {len(perfumes)} parfum kaydedildi: {output_path}")

    return perfumes


def convert_sample():
    """Ornek 10 parfumu donustur ve data/ klasorune kaydet"""
    cache_base = os.path.expanduser(
        '~/.cache/huggingface/hub/datasets--FragDBnet--fragrance-database/snapshots'
    )
    csv_path = None
    if os.path.exists(cache_base):
        snapshots = sorted(os.listdir(cache_base), reverse=True)
        if snapshots:
            csv_path = os.path.join(cache_base, snapshots[0], 'fragrances.csv')

    if not csv_path or not os.path.exists(csv_path):
        print("[FRAGDB] Once FragDB CSV'yi indirin:")
        print("  python -c \"from huggingface_hub import hf_hub_download;")
        print("  hf_hub_download('FragDBnet/fragrance-database', 'fragrances.csv', repo_type='dataset')\"")
        return

    perfumes = load_fragdb_csv(csv_path)
    output = os.path.join(os.path.dirname(__file__), 'data', 'fragdb_sample.json')
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(perfumes, f, ensure_ascii=False, indent=2)

    print(f"[FRAGDB] {len(perfumes)} ornek parfum -> {output}")
    for p in perfumes:
        print(f"  - {p['name']} ({p['brand']}) [{p['gender']}]")
    return perfumes


def merge_with_existing(fragdb_perfumes, existing_path=None):
    """FragDB'yi mevcut veritabaniyla birlestir (tekrar edenleri atla)"""
    from perfume_engine import _init_database, save_database, PERFUME_DATABASE

    _init_database()
    mevcut_isimler = {p['name'].lower() for p in PERFUME_DATABASE}

    yeni_perfumler = [p for p in fragdb_perfumes if p['name'].lower() not in mevcut_isimler]

    if yeni_perfumler:
        PERFUME_DATABASE.extend(yeni_perfumler)
        save_database()
        print(f"[FRAGDB] {len(yeni_perfumler)} yeni parfum eklendi. Toplam: {len(PERFUME_DATABASE)}")
    else:
        print("[FRAGDB] Eklenecek yeni parfum yok.")

    return PERFUME_DATABASE


if __name__ == '__main__':
    convert_sample()
