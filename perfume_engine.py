# ParfumAI — Parfüm Eşleme Motoru
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

import json
import os
import threading
import tempfile
import traceback
from datetime import datetime

PERFUME_DATABASE = []

# Skorlama sabitleri
SEZON_AGIRLIK = 0.3
SKOR_AGIRLIK = 0.7
PROFIL_MUK_KAR = 50
MUK_TOP = 33
MUK_MID = 33
MUK_BASE = 34
MUK_ORTA = 33  # alias for MUK_MID
MUK_DIP = 34   # alias for MUK_BASE
DOMINANT_ESIK = 40
ZAYIF_KATMAN_ESIK = 25
DOMINANT_CEZA = 15
KRITIK_SEVIYE = 10

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "perfume_database.json")
SEED_PATH = os.path.join(DATA_DIR, "perfumes.json")
DB_LOCK = threading.Lock()

def _init_database():
    global PERFUME_DATABASE
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    PERFUME_DATABASE = data
                    return data
    except (json.JSONDecodeError, FileNotFoundError):
        corrupted_path = DB_PATH + ".corrupted." + datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            os.rename(DB_PATH, corrupted_path)
            _write_audit("system", "RECOVER", "perfume_database", 0,
                        {"error": "corrupted_json"}, {"recovered_to": corrupted_path})
        except Exception:
            pass
    if os.path.exists(SEED_PATH):
        try:
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
                if isinstance(seed_data, list) and len(seed_data) > 0:
                    PERFUME_DATABASE = seed_data
                    save_database()
                    return PERFUME_DATABASE
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    save_database()
    return PERFUME_DATABASE

def save_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    with DB_LOCK:
        fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=DATA_DIR)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(PERFUME_DATABASE, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, DB_PATH)
        except Exception:
            os.unlink(tmp_path)
            raise

def _write_audit(actor, action, table_name, record_id, old_values=None, new_values=None):
    try:
        log_path = os.path.join(DATA_DIR, "audit_log.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "table": table_name,
            "record_id": record_id,
            "old_values": old_values,
            "new_values": new_values
        }
        with DB_LOCK:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

def check_critical_stock(perfume_name=None, old_stock=None, new_stock=None):
    try:
        if old_stock is not None and new_stock is not None:
            if isinstance(old_stock, bool) and isinstance(new_stock, bool):
                if old_stock and not new_stock:
                    _write_audit("system", "CRITICAL_STOCK", "perfume_database", 0,
                                {}, {"message": f"Stok bitti: {perfume_name}"})
            elif isinstance(old_stock, (int, float)) and isinstance(new_stock, (int, float)):
                if old_stock > 0 and new_stock <= 0:
                    _write_audit("system", "CRITICAL_STOCK", "perfume_database", 0,
                                {}, {"message": f"Stok bitti: {perfume_name}"})
                else:
                    CRITIK_SEVIYE = 10
                    if new_stock < CRITIK_SEVIYE:
                        _write_audit("system", "LOW_STOCK", "perfume_database", 0,
                                    {}, {"message": f"Stok azalıyor: {perfume_name} ({new_stock})"})
    except Exception:
        pass

class PerfumeMatchingEngine:
    def __init__(self):
        self.parfumler = _init_database()
        self.cache_dir = os.path.join(os.path.dirname(__file__), "data", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def find_matches(self, nota_profili, gender="unisex"):
        top_dominant = nota_profili.get("top_dominant", "citrus")
        middle_dominant = nota_profili.get("middle_dominant", "floral")
        base_dominant = nota_profili.get("base_dominant", "musk")
        top_pct = nota_profili.get("top_pct", 33)
        middle_pct = nota_profili.get("middle_pct", 33)
        base_pct = nota_profili.get("base_pct", 34)
        profile_type = nota_profili.get("profile_type", self._belirleme(top_pct, middle_pct, base_pct))

        scored = []
        for p in self.parfumler:
            if not self._gender_allowed(p["gender"], gender):
                continue
            sim = self._calculate_similarity(p, top_dominant, middle_dominant, base_dominant, top_pct, middle_pct, base_pct)
            bonus = 30 if p["gender"] == gender else (15 if p["gender"] == "unisex" and gender != "unisex" else 0)
            scored.append((sim + bonus, sim, p))

        scored.sort(key=lambda x: x[0], reverse=True)

        yazlik = [x for x in scored if x[2]["season"] == "yaz"]
        kislik = [x for x in scored if x[2]["season"] == "kis"]
        dort_mevsim = [x for x in scored if x[2]["season"] in ("dört_mevsim", "dort_mevsim")]

        def season_sort_key(season_list, weight_field):
            return sorted(season_list, key=lambda x: x[2]["profile"][weight_field] * SEZON_AGIRLIK + x[1] * SKOR_AGIRLIK, reverse=True)

        yazlik = season_sort_key(yazlik, "top_pct")
        kislik = season_sort_key(kislik, "base_pct")

        def balance_key(x):
            p = x[2]["profile"]
            return (PROFIL_MUK_KAR - abs(p["top_pct"] - MUK_TOP) - abs(p["middle_pct"] - MUK_ORTA) - abs(p["base_pct"] - MUK_DIP)) * SEZON_AGIRLIK + x[1] * SKOR_AGIRLIK
        dort_mevsim = sorted(dort_mevsim, key=balance_key, reverse=True)

        def pick_unique(candidates, count, exclude_names):
            result = []
            for _, _, p in candidates:
                if p["name"] not in exclude_names and len(result) < count:
                    result.append(p)
                    exclude_names.add(p["name"])
                if len(result) >= count:
                    break
            return result

        def fallback_fill(season_list, season_value, count, exclude_names, all_scored):
            result = list(season_list)
            if len(result) >= count:
                return result
            for _, _, p in all_scored:
                if p["season"] != season_value and (season_value == "dört_mevsim" or p["season"] != ("dört_mevsim" if season_value == "kis" else "dört_mevsim")):
                    if season_value == "yaz" and p["season"] not in ("yaz", "dört_mevsim", "dort_mevsim"):
                        continue
                    if season_value == "kis" and p["season"] not in ("kis", "dört_mevsim", "dort_mevsim"):
                        continue
                    if season_value in ("dört_mevsim", "dort_mevsim") and p["season"] not in ("dört_mevsim", "dort_mevsim"):
                        continue
                if p["name"] not in exclude_names and len(result) < count:
                    result.append(p)
                    exclude_names.add(p["name"])
                if len(result) >= count:
                    break
            return result

        used_names = set()
        oneri_yaz = pick_unique(yazlik, 3, used_names)
        oneri_kis = pick_unique(kislik, 3, used_names)
        oneri_dort = pick_unique(dort_mevsim, 3, used_names)

        oneri_yaz = fallback_fill(oneri_yaz, "yaz", 3, used_names, scored)
        oneri_kis = fallback_fill(oneri_kis, "kis", 3, used_names, scored)
        oneri_dort = fallback_fill(oneri_dort, "dört_mevsim", 3, used_names, scored)

        return {
            "yaz": oneri_yaz,
            "kis": oneri_kis,
            "dört_mevsim": oneri_dort,
            "profile_type": profile_type
        }

    def _gender_allowed(self, perfume_gender, user_gender):
        if user_gender == "unisex":
            return True
        if perfume_gender == "unisex":
            return True
        return perfume_gender == user_gender

    def _belirleme(self, top_pct, middle_pct, base_pct):
        max_pct = max(top_pct, middle_pct, base_pct)
        if max_pct >= 40:
            if max_pct == top_pct:
                return "Yaz-Kehribar (Top Note Agirlikli)"
            elif max_pct == base_pct:
                return "Kis-Derin (Base Note Agirlikli)"
            elif max_pct == middle_pct:
                return "Ilkbahar-Yaz (Middle Note Agirlikli)"
            else:
                return "Karma Profil"
        elif top_pct >= 35:
            return "Hafif Yaz Egilimli"
        elif base_pct >= 35:
            return "Hafif Kis Egilimli"
        elif top_pct >= 25 and middle_pct >= 25 and base_pct >= 20:
            return "4 Mevsim Unisex (Dengeli Profil)"
        else:
            return "Karma Profil"

    def _calculate_similarity(self, parfum, top_dom, mid_dom, base_dom, top_pct, mid_pct, base_pct):
        score = 0
        note_map = {
            "citrus": ["citrus", "bergamot", "lemon", "orange", "grapefruit", "mandarin", "lime", "yuzu", "tangerine", "blood_orange", "blood_mandarin", "green_tangerine", "green_mandarin", "bitter_orange"],
            "bergamot": ["bergamot"],
            "green": ["green", "grass", "leaf", "galbanum", "fig", "violet_leaf", "hay_top", "bamboo", "cucumber", "cane", "bay_leaf", "crystal_moss"],
            "aqua": ["aqua", "marine", "sea", "salt", "ozone", "calone", "ocean", "water", "caviar", "ice", "sea_water", "water_hyacinth", "seaweed"],
            "fruity_top": ["apple", "pear", "pineapple", "tropical", "berry", "melon", "cassis", "strawberry", "papaya", "goji", "quince", "cranberry", "blueberry", "nectarine", "rhubarb", "cloudberry", "red_apple", "fruity"],
            "aldehyde": ["aldehyde", "aldehydic", "soapy", "sparkling", "solar_notes"],
            "spice_top": ["pepper", "pink_pepper", "black_pepper", "chili", "elemi"],
            "aromatic_top": ["mint", "peppermint", "eucalyptus", "anis", "anise", "basil", "tarragon", "star_anise"],
            "floral": ["rose", "jasmine", "ylang", "orchid", "gardenia", "freesia", "lily", "carnation", "champaca", "violet", "peony", "magnolia", "hibiscus", "osmanthus", "lilac", "hyacinth", "wisteria", "cyclamen", "daisy", "hawthorn", "narcissus", "marigold", "buttercup", "bluebell", "lotus", "muguet", "syringa", "white_rose"],
            "white_floral": ["jasmine", "tuberose", "gardenia", "lily", "neroli", "orange_blossom", "stephanotis", "honeysuckle"],
            "spice_mid": ["cinnamon", "clove", "cardamom", "ginger", "nutmeg", "saffron", "coriander", "caraway", "cumin", "mace", "paprika", "spice"],
            "herbal": ["lavender", "sage", "rosemary", "thyme", "basil", "mint", "chamomile", "clary_sage", "geranium", "angelica", "cannabis", "myrtle", "tea", "white_thyme", "nard"],
            "fruity_mid": ["peach", "apricot", "plum", "raspberry", "lychee", "blackberry", "cherry", "apple_mid", "pear_mid", "black_currant", "pomegranate", "mirabelle", "red_fruit"],
            "powdery": ["iris", "violet", "almond", "heliotrope", "powdery", "orris", "mimosa", "bitter_almond", "licorice"],
            "honey_tobacco": ["honey", "tobacco_blossom", "beeswax", "hay", "broom"],
            "woody_mid": ["cedar_mid", "sandalwood_mid", "pine_mid", "cashmeran_mid", "cedar", "sandalwood"],
            "woody": ["cedar", "sandalwood", "pine", "woody", "cashmeran", "cypress", "juniper", "akigalawood", "guaiac_wood", "teak", "rosewood", "wood"],
            "amber": ["amber", "ambroxan", "ambergris", "labdanum", "golden_amber", "succinic", "ambre", "cistus", "iso_e_super"],
            "vanilla_gourmand": ["vanilla", "tonka", "benzoin", "caramel", "praline", "cocoa", "chocolate", "sugar", "cotton_candy", "almond", "coffee", "coconut", "cognac", "rum", "pistachio", "chestnut"],
            "musk": ["musk", "white_musk", "vegetal_musk", "silky_musk", "ambrette"],
            "leather": ["leather", "suede", "isobutyl_quinoline", "birch_tar", "styrax", "asphalt"],
            "oud": ["oud", "agarwood", "oudh"],
            "patchouli_earthy": ["patchouli", "earthy", "soil", "moss", "oakmoss", "tree_moss", "vetiver", "mineral", "truffle", "fir_resin"],
            "incense_tobacco": ["incense", "frankincense", "myrrh", "tobacco", "hay", "dried_fruit", "raisin", "olibanum"]
        }

        # 1) Dominant note matching — strong signal
        note_layers = [
            (top_dom, parfum["notes_top"]),
            (mid_dom, parfum["notes_middle"]),
            (base_dom, parfum["notes_base"])
        ]
        for dom, notes in note_layers:
            if dom in note_map:
                for keyword in note_map[dom]:
                    for p_note in notes:
                        if keyword == p_note or p_note.startswith(keyword + "_") or keyword.startswith(p_note + "_"):
                            score += 10
                            break

        # 2) Profile percentage similarity — PRIMARY differentiator
        pct_diff = abs(parfum["profile"]["top_pct"] - top_pct) + \
                   abs(parfum["profile"]["middle_pct"] - mid_pct) + \
                   abs(parfum["profile"]["base_pct"] - base_pct)
        score += max(0, PROFIL_MUK_KAR - pct_diff)

        # 3) Penalty for mismatched dominant layer
        p_top = parfum["profile"]["top_pct"]
        p_mid = parfum["profile"]["middle_pct"]
        p_base = parfum["profile"]["base_pct"]
        if top_pct > DOMINANT_ESIK and p_top < ZAYIF_KATMAN_ESIK:
            score -= DOMINANT_CEZA
        if mid_pct > DOMINANT_ESIK and p_mid < ZAYIF_KATMAN_ESIK:
            score -= DOMINANT_CEZA
        if base_pct > DOMINANT_ESIK and p_base < ZAYIF_KATMAN_ESIK:
            score -= DOMINANT_CEZA

        return score

    def search_fragrantica(self, query, max_results=5):
        from scraper.external_search import search_fragrantica as _search_fragrantica
        return _search_fragrantica(query, max_results)

    def search_parfumo(self, query, max_results=5):
        from scraper.external_search import search_parfumo as _search_parfumo
        return _search_parfumo(query, max_results)

# Global matching engine instance (used by routes)
matching_engine = PerfumeMatchingEngine()
