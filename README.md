04 — Restoran Rezervasyon Sistemi

Flask + SQLite. 10 masa, 12:00–22:00 saat dilimleri. Çakışma kontrolü (aynı masa+tarih+saat tek rezervasyon).

## Çalıştır
```bash
pip install -r requirements.txt
python app.py
```
http://localhost:5000 → tarih/saat seç, boş masaya rezervasyon yap, iptal et.


<!-- hardened-config -->
## Yapılandırma & Üretim

Ayarlar ortam değişkenlerinden okunur (`.env.example` dosyasına bakın):

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `SECRET_KEY` | dev fallback | Oturum imzalama anahtarı — **üretimde mutlaka değiştirin** |
| `HOST` | `127.0.0.1` | Dinlenecek arayüz |
| `PORT` | `5000` | Port |
| `FLASK_DEBUG` | `0` | `1` = geliştirme modu (üretimde `0`) |

```bash
pip install -r requirements.txt
cp .env.example .env        # değerleri düzenleyin

# Geliştirme
python app.py

# Üretim (waitress, çapraz platform WSGI sunucusu)
waitress-serve --listen=0.0.0.0:5000 app:app
```
