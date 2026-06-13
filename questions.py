# ParfumAI — Soru Veritabanı
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

QUESTIONS = [
    {
        "id": "gender",
        "category": "Temel Profil",
        "icon": "bi bi-person",
        "question": "Kendinizi hangi cinsiyet kimliğiyle tanımlıyorsunuz?",
        "subtext": "Bu bilgi, size en uygun parfümleri seçmek için kullanılır.",
        "reference": "",
        "technique": "",
        "required": True,
        "options": [
            {"text": "Kadın", "icon": "bi bi-gender-female", "scores": {"gender_female": 1}},
            {"text": "Erkek", "icon": "bi bi-gender-male", "scores": {"gender_male": 1}},
            {"text": "Fark etmez", "icon": "bi bi-shuffle", "scores": {"gender_unisex": 1}}
        ]
    },
    {
        "id": 1,
        "category": "Ruh Hali",
        "icon": "bi bi-emoji-smile",
        "question": "Bu koku sizi hangi ruh haline taşısın?",
        "subtext": "Limbik sistem, koku moleküllerini doğrudan duygusal merkeze iletir (Herz, 2009).",
        "reference": "Herz, R.S. (2009). Aromatherapy Facts and Fictions. Int. J. Neuroscience.",
        "technique": "Nöroaromatik Duygu Haritalaması",
        "options": [
            {"text": "Enerjik ve canlı", "icon": "bi bi-sun", "scores": {"top_citrus": 15, "top_bergamot": 10}},
            {"text": "Romantik ve yumuşak", "icon": "bi bi-heart", "scores": {"middle_floral": 15, "middle_white_floral": 10}},
            {"text": "Sakin ve huzurlu", "icon": "bi bi-moon", "scores": {"base_musk": 15, "base_amber": 10}},
            {"text": "Gizemli ve çekici", "icon": "bi bi-eye", "scores": {"middle_spice_mid": 15, "base_oud": 10}}
        ]
    },
    {
        "id": 4,
        "category": "Yayılım",
        "icon": "bi bi-broadcast",
        "question": "Parfümün ne kadar hissedilmeli?",
        "subtext": "Sillage, moleküler ağırlığa ve buharlaşma hızına bağlıdır.",
        "reference": "Jellinek, P. (1997). The Psychological Basis of Perfumery.",
        "technique": "Parfüm Piramidi Bilimi",
        "options": [
            {"text": "Hafif, sadece ben", "icon": "bi bi-emoji-smile", "scores": {"base_musk": 15, "base_vanilla_gourmand": 10}},
            {"text": "Yakın çevrem hissetsin", "icon": "bi bi-people", "scores": {"middle_floral": 15, "middle_spice_mid": 10}},
            {"text": "Net biçimde fark edilsin", "icon": "bi bi-volume-up", "scores": {"middle_powdery": 15, "top_aldehyde": 10}},
            {"text": "Herkes bilsin", "icon": "bi bi-megaphone", "scores": {"middle_spice_mid": 15, "base_incense_tobacco": 10}}
        ]
    },
    {
        "id": 6,
        "category": "Tatlılık",
        "icon": "bi bi-droplet",
        "question": "Kokunun tatlılık seviyesi?",
        "subtext": "Tatlı koku molekülleri opioid sistemini aktive ederek ödül hissi yaratır.",
        "reference": "Herz, R.S. (2009). Aromatherapy Facts and Fictions.",
        "technique": "Koku-Hedonik Korelasyon",
        "options": [
            {"text": "Ferah ve ekşi", "icon": "bi bi-droplet-half", "scores": {"top_citrus": 15, "top_green": 10}},
            {"text": "Baharatlı ve sıcak", "icon": "bi bi-fire", "scores": {"middle_spice_mid": 15, "middle_herbal": 10}},
            {"text": "Tatlı ve kremsi", "icon": "bi bi-cupcake", "scores": {"base_vanilla_gourmand": 15, "base_amber": 10}},
            {"text": "Topraksı ve doğal", "icon": "bi bi-tree", "scores": {"middle_herbal": 15, "base_patchouli_earthy": 10}}
        ]
    },
    {
        "id": 7,
        "category": "Karakter",
        "icon": "bi bi-person-badge",
        "question": "Kokun nasıl bir karakter yansıtsın?",
        "subtext": "Big Five kişilik modeline göre koku tercihleri değişir (Janssens & De Pelsmacker).",
        "reference": "Janssens, W. & De Pelsmacker, P. Smells Like Me: Personality and Perfume Choice.",
        "technique": "Big Five-Koku Eşleme Modeli",
        "options": [
            {"text": "Doğal ve sade", "icon": "bi bi-leaf", "scores": {"top_green": 15, "top_citrus": 10}},
            {"text": "Klasik ve zarif", "icon": "bi bi-gem", "scores": {"middle_powdery": 15, "middle_floral": 10}},
            {"text": "Gizemli ve derin", "icon": "bi bi-moon-stars", "scores": {"base_incense_tobacco": 15, "base_amber": 10}},
            {"text": "Modern ve cesur", "icon": "bi bi-lightning", "scores": {"middle_spice_mid": 15, "base_oud": 10}}
        ]
    },
    {
        "id": 11,
        "category": "Koku Ailesi",
        "icon": "bi bi-circle",
        "question": "En çok hangi koku ailesine yakın hissediyorsun?",
        "subtext": "Parfüm çarkı 4 ana aileyi kapsar. Bu, beklenen tercihinizi gösterir.",
        "reference": "Jellinek, P. (1949). The Practice of Modern Perfumery.",
        "technique": "Jellinek Parfüm Çarkı",
        "options": [
            {"text": "Ferah ve sucul", "icon": "bi bi-water", "scores": {"top_aqua": 15, "top_citrus": 10}},
            {"text": "Çiçeksi ve romantik", "icon": "bi bi-flower1", "scores": {"middle_floral": 15, "middle_white_floral": 10}},
            {"text": "Odunsu ve sağlam", "icon": "bi bi-tree", "scores": {"base_woody": 15, "base_amber": 10}},
            {"text": "Oryantal ve gizemli", "icon": "bi bi-moon", "scores": {"middle_spice_mid": 15, "base_oud": 10}}
        ]
    },
    {
        "id": 12,
        "category": "Yapı",
        "icon": "bi bi-layers",
        "question": "Parfümün yapısı nasıl olsun?",
        "subtext": "Karmaşık kokular zaman içinde farklı beyin bölgelerini sırasıyla uyarır.",
        "reference": "Herz, R.S. (2009). Aromatherapy Facts and Fictions.",
        "technique": "Nörokimyasal Yolculuk Tasarımı",
        "options": [
            {"text": "Sade ve minimal", "icon": "bi bi-dash", "scores": {"top_citrus": 15, "top_green": 10}},
            {"text": "Dengeli", "icon": "bi bi-plus", "scores": {"middle_floral": 15, "middle_herbal": 10}},
            {"text": "Karmaşık ve katmanlı", "icon": "bi bi-layers-half", "scores": {"base_incense_tobacco": 15, "base_oud": 10}},
            {"text": "Tatlı ve sıcak", "icon": "bi bi-thermometer-half", "scores": {"middle_powdery": 15, "base_vanilla_gourmand": 10}}
        ]
    }
]

IN_STORE_QUESTIONS = [q for q in QUESTIONS if q["id"] != "gender"]

def get_regular_questions():
    return IN_STORE_QUESTIONS

def get_gender_question():
    return next((q for q in QUESTIONS if q["id"] == "gender"), None)
