# ParfumAI — Kişisel Koku Profili & Parfüm Öneri Sistemi

**Flask tabanlı, yapay zeka destekli (isteğe bağlı) parfüm öneri motoru.**

Anket yanıtlarınıza göre koku profilinizi çıkarır, 342 parfüm arasından cinsiyet ve mevsime duyarlı eşleşmeler sunar. Gemini ya da OpenRouter API ile her öneri için yapay zeka açıklaması alabilirsiniz. API anahtarı olmadan da şablon tabanlı açıklamalarla çalışır.

## Özellikler

- **Çift Yönlü Anket** — Başlangıç (6 basit soru) ve İleri (4 adımlı detaylı seçim) olmak üzere iki ayrı yol
- **Koku Profili Analizi** — Üst/orta/alt nota dağılımınızı belirler
- **Akıllı Eşleştirme** — Cinsiyet, mevsim, nota uyumuna göre 9 parfüm (3 yaz + 3 kış + 3 4 mevsim)
- **AI Açıklamaları** — Gemini / OpenRouter API ile "Neden bu parfüm?" (opsiyonel, şablon yedekli)
- **Otomatik Görsel** — Her parfüme dark-neon temalı gradient görsel (Pillow ile üretilir)
- **Radar Grafik** — 5 eksenli koku profili görselleştirmesi
- **Yönetici Paneli** — Parfüm ekleme/silme/düzenleme
- **SEO & Paylaşım** — QR kod, WhatsApp, panoya kopyala
- **CSRF Korumalı** — Tüm POST uç noktalarında
- **AI olmadan da çalışır** — API anahtarı gerekmez, şablon açıklamalar hazır

## Hızlı Başlangıç

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python app.py

# Tarayıcıda aç
http://127.0.0.1:5001
```

- **Giriş:** `admin` / `admin123` (`.env` ile değiştirin)
- **AI Özelliği:** `.env` dosyasına `GEMINI_API_KEY` ya da `OPENROUTER_API_KEY` ekleyin (opsiyonel)

## Proje Yapısı

```
perfume-advisor/
├── app.py                 # Flask ana uygulama
├── perfume_engine.py      # 342 parfüm veritabanı + eşleştirme motoru
├── ai_service.py          # Gemini / OpenRouter AI + şablon yedek
├── ml_similarity.py       # Benzerlik matrisi (ön hesaplama)
├── utils.py               # CSRF, dekoratörler
├── legacy/
│   ├── questions.py       # Anket soruları
│   └── scoring.py         # Nota skorlama motoru
├── routes/
│   ├── main.py            # Sayfa route'ları
│   ├── api.py             # API route'ları
│   └── admin.py           # Admin route'ları
├── templates/             # Jinja2 şablonları
├── static/                # CSS, JS, vendor kütüphaneler
└── tests/                 # Pytest testleri (16 test)
```

## API Uç Noktaları

| Yöntem | Uç Nokta | Açıklama |
|--------|----------|----------|
| GET | `/` | Ana sayfa |
| GET | `/survey` | Koku anketi (çift yönlü) |
| POST | `/api/submit` | İleri seviye anket yanıtlarını gönder |
| POST | `/api/submit-simple` | Başlangıç seviyesi anket yanıtlarını gönder |
| GET | `/results` | Sonuçlar sayfası |
| POST | `/api/explain` | AI açıklaması (opsiyonel, şablon yedekli) |
| GET | `/api/questions` | Anket soruları (JSON) |
| GET | `/api/stock` | Stok durumu |
| POST | `/api/log-sale` | Satış kaydet |
| GET | `/admin` | Yönetici paneli |

## AI Entegrasyonu

API anahtarı olmadan da çalışır — şablon tabanlı açıklamalar hazırdır.

Etkinleştirmek için (isteğe bağlı):

```bash
# 1. .env.example dosyasını .env olarak kopyalayın
# 2. Aşağıdakilerden birini doldurun:
#    GEMINI_API_KEY=...     -> https://aistudio.google.com/app/apikey
#    OPENROUTER_API_KEY=... -> https://openrouter.ai/keys
# 3. (isteğe bağlı) AI_PROVIDER=openrouter (varsayılan: google)
```

## Güvenlik

- `.env` dosyası (API anahtarları) asla commit edilmez — `.gitignore` ile korunur
- Tüm POST uç noktaları CSRF token ile korunur
- Admin oturumu session bazlıdır
- Ham veritabanı dosyaları (`data/`) git dışındadır

## Test

```bash
pytest tests/ -v
# 16 testin tamamı geçmeli
```

## Lisans

**All Rights Reserved** — Ahmet Rıfai Kuyucu

Bu yazılımın izinsiz kopyalanması, dağıtılması, ticari kullanımı yasaktır. Detaylı bilgi için [LICENSE](LICENSE) dosyasına bakınız.
