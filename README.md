# ParfumAI — Kişisel Koku Analizi & Parfüm Öneri Sistemi

**Flask tabanlı, yapay zeka destekli parfüm öneri motoru.**

Anket yanıtlarınıza göre koku profilinizi çıkarır, 340+ parfüm arasından size özel eşleşmeler sunar. İsteğe bağlı Gemini API ile her öneri için AI açıklaması alabilirsiniz.

## Özellikler

- **Koku Profili Analizi** — 7 soruluk anketle üst/orta/alt nota dağılımınızı belirler
- **Akıllı Eşleştirme** — Cinsiyet, mevsim, nota uyumuna göre 9 parfüm (3 yaz + 3 kış + 3 dört mevsim)
- **AI Açıklamaları** — Gemini API entegrasyonu ile "Neden bu parfüm?" açıklaması (opsiyonel)
- **Radar Grafik** — 5 eksenli koku profili görselleştirmesi
- **Yönetici Paneli** — Parfüm ekleme/silme/düzenleme, stok takibi
- **Satış Kaydı** — CSV log ve istatistikler
- **Harici Arama** — Fragrantica ve Parfumo bağlantıları
- **QR & WhatsApp Paylaşım**

## Hızlı Başlangıç

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python app.py

# Tarayıcıda aç
http://127.0.0.1:5000
```

- **Giriş:** `admin` / `admin123` (değiştirmek için `ADMIN_PASSWORD` ortam değişkeni)
- **AI Özelliği:** `.env` dosyasına `GEMINI_API_KEY=...` ekleyin (opsiyonel)

## Proje Yapısı

```
perfume-advisor/
├── app.py                # Flask ana uygulama
├── perfume_engine.py     # 340+ parfüm veritabanı + eşleştirme
├── ai_service.py         # Gemini / OpenRouter AI entegrasyonu
├── scoring.py            # Nota skorlama motoru
├── questions.py          # Anket soruları
├── templates/            # Jinja2 şablonları
├── static/               # CSS, JS, vendor kütüphaneler
└── tests/                # Pytest testleri
```

## API Uç Noktaları

| Yöntem | Uç Nokta | Açıklama |
|--------|----------|----------|
| GET | `/` | Ana sayfa |
| GET | `/survey` | Koku anketi |
| POST | `/api/submit` | Anket yanıtlarını gönder |
| GET | `/results` | Sonuçlar sayfası |
| POST | `/api/explain` | AI açıklaması (API key gerekli) |
| GET | `/api/questions` | Anket soruları (JSON) |
| GET | `/api/stock` | Stok durumu |
| POST | `/api/log-sale` | Satış kaydet |
| GET | `/admin` | Yönetici paneli |

## AI Entegrasyonu

Varsayılan olarak AI özellikleri **pasiftir**. Etkinleştirmek için:

1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden ücretsiz API key alın
2. `.env.example` dosyasını `.env` olarak kopyalayın
3. `GEMINI_API_KEY=` satırına key'inizi yazın
4. Uygulamayı yeniden başlatın

Desteklenen sağlayıcılar: **Google Gemini** (önerilen), **OpenRouter** (opsiyonel).

## Test

```bash
pytest tests/ -v
# 16 testin tamamı geçmeli
```

## Lisans

**All Rights Reserved** — Ahmet Rıfai Kuyucu

Bu yazılımın izinsiz kopyalanması, dağıtılması, ticari kullanımı yasaktır. Detaylı bilgi için [LICENSE](LICENSE) dosyasına bakınız.
