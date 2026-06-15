# ParfumAI — AI Servis Modülü
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.
#
# Bu modül, parfüm önerilerine AI destekli açıklamalar ekler.
# Kullanmak için:
#   1. .env dosyasına GEMINI_API_KEY ekleyin
#   2. Veya doğrudan ai_service.py'de PROVIDER ayarlayın
#
# Desteklenen sağlayıcılar:
#   - google (Gemini 2.0 Flash) — ücretsiz, önerilen
#   - openrouter (Gemini 2.0 Flash ücretsiz API üzerinden)

import os
import json
import re
from datetime import datetime

# ============================================================
# KONFİGÜRASYON
# ============================================================
# API key'inizi buraya girebilir veya .env dosyasından yükleyebilirsiniz.
# Boş bırakılırsa AI özellikleri pasif kalır, uygulama normal çalışır.

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Varsayılan sağlayıcı: "google" veya "openrouter"
PROVIDER = os.environ.get("AI_PROVIDER", "google")

# ============================================================
# AI AÇIKLAMA ÜRETİCİ
# ============================================================

def generate_explanations(note_profile, recommendations, gender, name="Misafir"):
    """Kullanıcının profiline göre parfüm önerilerine AI açıklaması ekler.

    Parametreler:
        note_profile (dict): Kullanıcının nota profili
        recommendations (dict): {yaz: [...], kis: [...], dört_mevsim: [...]}
        gender (str): "kadın" / "erkek" / "unisex"
        name (str): Kullanıcı adı

    Dönüş:
        dict: Her parfüme eklenmiş ai_açıklama alanı
        veya AI yoksa şablon açıklama döner
    """
    profile_text = _profile_to_text(note_profile)

    if _ai_available():
        prompt = _build_prompt(profile_text, recommendations, gender, name)
        try:
            if PROVIDER == "openrouter":
                raw = _call_openrouter(prompt)
            else:
                raw = _call_gemini(prompt)
            result = _parse_response(raw, recommendations)
            if result:
                return result
        except Exception as e:
            print(f"[AI] API hatası, şablon kullanılıyor ({e})")

    # Şablon tabanlı açıklama (API yoksa veya hata alırsa)
    try:
        return _template_explanations(note_profile, recommendations, name)
    except Exception as e:
        print(f"[AI] Şablon hatası: {e}")
        return {}


def _ai_available():
    if PROVIDER == "google" and GEMINI_API_KEY:
        return True
    if PROVIDER == "openrouter" and OPENROUTER_API_KEY:
        return True
    return False


def _profile_to_text(np):
    """Nota profilini okunabilir metne çevirir."""
    top = np.get("top_dominant", "bilinmiyor")
    mid = np.get("middle_dominant", "bilinmiyor")
    base = np.get("base_dominant", "bilinmiyor")
    tp = np.get("top_pct", 33)
    mp = np.get("middle_pct", 33)
    bp = np.get("base_pct", 34)
    ptype = np.get("profile_type", "Karma")

    return (
        f"Kullanıcının kokusal profili: {ptype}. "
        f"Nota dağılımı: Üst notalar %{tp} ({top}), "
        f"Orta notalar %{mp} ({mid}), "
        f"Alt notalar %{bp} ({base})."
    )


def _build_prompt(profile_text, recommendations, gender, name):
    """AI'a gönderilecek prompt'u oluşturur."""
    perfumes_text = ""
    for season, plist in recommendations.items():
        if not isinstance(plist, list):
            continue
        label = {"yaz": "Yaz", "kis": "Kış", "dört_mevsim": "4 Mevsim"}.get(season, season)
        perfumes_text += f"\n{label}:\n"
        for p in plist[:3]:
            nt = ", ".join(p.get("notes_top", [])[:3])
            nm = ", ".join(p.get("notes_middle", [])[:3])
            nb = ", ".join(p.get("notes_base", [])[:3])
            perfumes_text += (
                f"  - {p['brand']} {p['name']} "
                f"(Üst: {nt}, Orta: {nm}, Alt: {nb})\n"
            )

    return (
        f"Sen bir parfüm danışmanısın. {name} isimli müşteri için "
        f"({gender}) aşağıdaki koku profiline göre önerilen parfümleri "
        f"kısa ve ikna edici şekilde açıkla.\n\n"
        f"{profile_text}\n"
        f"Önerilen parfümler:{perfumes_text}\n\n"
        f"Her parfüm için 1-2 cümlelik neden önerildiğini açıkla. "
        f"Kullanıcının koku profiliyle bağlantı kur. "
        f"Samimi ama profesyonel ol. Türkçe cevap ver.\n\n"
        f"CEVAP FORMATI (JSON):\n"
        f"{{\n"
        f'  "açıklamalar": [\n'
        f'    {{"parfüm": "marka adı", "neden": "açıklama"}},\n'
        f"    ...\n"
        f"  ]\n"
        f"}}\n\n"
        f"SADECE JSON döndür, başka bir şey yazma."
    )


def _call_gemini(prompt):
    """Google Gemini API çağrısı."""
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


def _call_openrouter(prompt):
    """OpenRouter API çağrısı (ücretsiz modeller)."""
    import requests
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _parse_response(raw, recommendations):
    """AI yanıtını parse edip parfüm isimlerine göre eşler."""
    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return {}
        data = json.loads(json_match.group())
        explanations = {}
        for item in data.get("açıklamalar", []):
            key = item.get("parfüm", "").lower().strip()
            explanations[key] = item.get("neden", "")

        result = {}
        for season, plist in recommendations.items():
            if not isinstance(plist, list):
                continue
            for p in plist[:3]:
                pname = p.get("name", "").lower()
                brand = p.get("brand", "").lower()
                for key in [f"{brand} {pname}", pname]:
                    if key in explanations:
                        result[p.get("name", "")] = explanations[key]
                        break
        return result
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return {}


def _template_explanations(note_profile, recommendations, name):
    """API olmadığında şablon tabanlı açıklama üretir."""
    ptype = note_profile.get("profile_type", "Karma")
    top = note_profile.get("top_dominant", "citrus")
    mid = note_profile.get("middle_dominant", "floral")
    base = note_profile.get("base_dominant", "musk")

    templates = {
        "Taze": [
            f"{name}, ferah ve canlı üst notaları ({top}) seven bir profile sahip. Bu parfüm, taze açılışıyla size enerji verecek.",
            f"Canlı ve dinamik kokuları tercih ediyorsunuz. Bu öneri, {top} ve {mid} notalarının mükemmel dengesini sunuyor.",
            f"Enerjik yapınıza en uygun seçeneklerden biri. {top} üst notalarıyla güne ferah bir başlangıç yapın."
        ],
        "Dengeli": [
            f"{name}, dengeli bir koku profiline sahip. Bu parfüm, {top}, {mid} ve {base} notaları arasında uyumlu bir geçiş sunar.",
            f"Klasik ve her daim şık bir tercih. {mid} kalp notaları size zarif bir hava katacak.",
            f"Her ortama uyum sağlayabilecek bu seçenek, {base} temel notalarıyla kalıcı bir iz bırakır."
        ],
        "Derin": [
            f"{name}, derin ve etkileyici kokulardan hoşlanıyor. {base} alt notaları bu parfümün karakterini belirliyor.",
            f"Gizemli ve çekici bir profil. Bu parfüm, {mid} ve {base} notalarıyla sofistike bir deneyim vaat ediyor.",
            f"Etkileyici bir koku arayışınızda, {base} notalarının sıcaklığı ve derinliği sizi saracak."
        ],
        "Karma": [
            f"{name}, çok yönlü bir koku zevkine sahip. Bu parfüm, {top} ile {base} arasında keyifli bir yolculuk sunar.",
            f"Farklı notaları bir arada sevenler için ideal. {mid} kalp notaları öne çıkıyor.",
            f"Her mevsime uygun bu seçenek, {top} ve {base} dengesiyle her anınıza eşlik eder."
        ]
    }

    ptype_key = "Taze" if "taze" in ptype.lower() else "Dengeli" if "dengeli" in ptype.lower() else "Derin" if "derin" in ptype.lower() else "Karma"
    pool = templates.get(ptype_key, templates["Karma"])

    result = {}
    for season, plist in recommendations.items():
        if not isinstance(plist, list):
            continue
        for i, p in enumerate(plist[:3]):
            result[p["name"]] = pool[i % len(pool)]

    return result
