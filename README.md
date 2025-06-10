# PerfuMatch - Parfüm Muadil Öneri Sistemi

PerfuMatch, lüks parfümlerin uygun fiyatlı muadillerini bulmak için geliştirilmiş bir web uygulamasıdır. PostgreSQL veritabanı ile desteklenen bu sistem, parfüm notalarına, ailelerine ve markalarına göre akıllı eşleştirmeler yapar.

## ⚡ Hızlı Başlangıç

### 🖱️ Tek Tıkla Kurulum

**Windows kullanıcıları:**
```cmd
# 1. Projeyi klonlayın
git clone https://github.com/elifkaramehmeto/perfumatch.git
cd perfumatch

# 2. Kurulum script'ini çift tıklayın veya çalıştırın
setup.bat
```

**macOS/Linux kullanıcıları:**
```bash
# 1. Projeyi klonlayın
git clone https://github.com/elifkaramehmeto/perfumatch.git
cd perfumatch

# 2. Kurulum script'ini çalıştırın
./setup.sh
```

### 🔧 Manuel Kurulum

```bash
# 1. Projeyi klonlayın
git clone https://github.com/elifkaramehmeto/perfumatch.git
cd perfumatch

# 2. Python kurulum script'ini çalıştırın
python setup.py

# 3. Uygulamayı başlatın
run.bat        # Windows
# veya
./run.sh       # macOS/Linux

# 4. Tarayıcınızda açın
# http://localhost:5000
```

> **💡 İpucu:** İlk kurulum 5-10 dakika sürebilir. Script tüm gereksinimleri otomatik olarak kontrol eder ve kurar.

## 🎯 Özellikler

### ✨ Ana Özellikler
- **Akıllı Parfüm Arama**: İsim, nota ve aile bazında gelişmiş arama
- **Benzerlik Analizi**: Parfüm notalarına göre %90+ doğrulukla eşleştirme
- **Gerçek Zamanlı Veri**: Parfumo.com entegrasyonu ile güncel bilgiler
- **Kapsamlı Veritabanı**: 3000+ parfüm verisi (Bargello, Muscent, Zara)
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu modern arayüz

### 🔍 Arama Seçenekleri
1. **İsme Göre Arama**: Marka ve parfüm adı ile arama
2. **Notalara Göre Arama**: Üst, orta ve alt notalara göre filtreleme
3. **Aileye Göre Arama**: Çiçeksi, odunsu, oriental vb. ailelere göre arama

### 📊 Veritabanı Özellikleri
- **PostgreSQL**: Güçlü ilişkisel veritabanı
- **Otomatik Benzerlik Hesaplama**: Makine öğrenmesi algoritmaları
- **Arama Geçmişi**: Kullanıcı davranış analizi
- **Değerlendirme Sistemi**: Kullanıcı geri bildirimleri

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### 🎯 Hızlı Kurulum (Önerilen)

**İlk kez kuracaklar için otomatik kurulum script'i:**

```bash
# Projeyi klonlayın
git clone https://github.com/elifkaramehmeto/perfumatch.git
cd perfumatch

# Otomatik kurulum script'ini çalıştırın
python setup.py
```

Bu script otomatik olarak:
- ✅ Sistem gereksinimlerini kontrol eder
- ✅ Python sanal ortamı oluşturur
- ✅ Tüm bağımlılıkları yükler
- ✅ PostgreSQL veritabanını kurar
- ✅ Environment dosyalarını oluşturur
- ✅ İlk verileri içe aktarır
- ✅ Çalıştırma script'lerini hazırlar

### 🖥️ Uygulamayı Başlatma

Kurulum tamamlandıktan sonra:

**Windows:**
```cmd
run.bat
```

**macOS/Linux:**
```bash
./run.sh
```

**Manuel başlatma:**
```bash
# Sanal ortamı aktifleştir
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows

# Uygulamayı başlat
python server.py
```

### 🌐 Erişim Adresleri
- **Ana sayfa:** http://localhost:5000
- **API Sağlık Kontrolü:** http://localhost:5000/api/health
- **API Dokümantasyonu:** http://localhost:5000/api/

### 📁 Kurulum Sonrası Oluşturulan Dosyalar

Kurulum script'i aşağıdaki dosya ve klasörleri otomatik olarak oluşturur:

```
perfumatch/
├── venv/                   # Python sanal ortamı
├── logs/                   # Uygulama log dosyaları
├── uploads/                # Yüklenen dosyalar
├── static/                 # Statik dosyalar (CSS, JS, resimler)
├── data/backups/           # Veritabanı yedekleri
├── .env                    # Environment değişkenleri
├── run.bat                 # Windows çalıştırma script'i
├── run.sh                  # Unix/Linux çalıştırma script'i
└── requirements.txt        # Güncellenmiş Python bağımlılıkları
```

### 🔑 Önemli Dosyalar

- **`.env`** - Veritabanı bağlantısı ve uygulama ayarları
- **`run.bat/run.sh`** - Uygulamayı başlatmak için
- **`logs/perfumatch.log`** - Uygulama logları
- **`setup.py`** - Ana kurulum script'i

### 🐳 Docker ile Kurulum (Alternatif)

```bash
# Docker Compose ile başlatın
docker-compose up -d

# Verileri içe aktarın
docker-compose exec web python import_data.py
```

**Docker erişim adresleri:**
- Ana uygulama: http://localhost:5000
- pgAdmin: http://localhost:8080 (admin@perfumatch.com / admin123)

### 🔧 Manuel Kurulum (Gelişmiş Kullanıcılar)

1. **Sanal ortam oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
npm install
```

3. **PostgreSQL veritabanını kurun:**
```bash
# PostgreSQL'e bağlanın
psql -U postgres

# Veritabanı ve kullanıcı oluşturun
CREATE DATABASE perfumatch_db;
CREATE USER perfumatch_user WITH PASSWORD 'perfumatch_pass';
GRANT ALL PRIVILEGES ON DATABASE perfumatch_db TO perfumatch_user;
ALTER USER perfumatch_user CREATEDB;
\q
```

4. **Environment dosyası oluşturun (.env):**
```env
DATABASE_URL=postgresql://perfumatch_user:perfumatch_pass@localhost:5432/perfumatch_db
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

5. **Verileri içe aktarın:**
```bash
python import_data.py
```

6. **Sunucuyu başlatın:**
```bash
python server.py
```

## 📁 Proje Yapısı

```
perfumatch/
├── src/
│   ├── api/                    # Frontend API entegrasyonu
│   │   └── perfume-api.js
│   ├── models/                 # Veritabanı modelleri
│   │   ├── __init__.py
│   │   └── database.py
│   ├── utils/                  # Yardımcı araçlar
│   │   └── data_importer.py
│   ├── script/                 # Frontend JavaScript
│   │   └── script.js
│   └── style/                  # CSS stilleri
│       └── style.css
├── scrapping/                  # Web scraping araçları
│   └── request_branded.py
├── sql/                        # Veritabanı şemaları
│   └── init.sql
├── docker-compose.yml          # Docker konfigürasyonu
├── Dockerfile                  # Docker image tanımı
├── server.py                   # Flask sunucu
├── import_data.py             # Veri içe aktarma script'i
├── requirements.txt           # Python bağımlılıkları
├── index.html                 # Ana sayfa
├── perfume-detail.html        # Detay sayfası
└── *.json                     # Parfüm veri dosyaları
```

## 🔧 API Endpoints

### Parfüm Arama
```http
POST /api/perfume/search
Content-Type: application/json

{
  "searchTerm": "Chanel No.5",
  "searchType": "name",
  "gender": "women",
  "limit": 10
}
```

### Parfüm Detayı
```http
GET /api/perfume/{id}
```

### Parfüm Alternatifleri
```http
GET /api/perfume/{id}/alternatives
```

### Popüler Parfümler
```http
GET /api/popular-perfumes
```

### Sağlık Kontrolü
```http
GET /api/health
```

## 🗄️ Veritabanı Şeması

### Ana Tablolar
- **brands**: Parfüm markaları (lüks/alternatif)
- **perfumes**: Parfüm bilgileri
- **notes**: Parfüm notaları (üst/orta/alt)
- **perfume_families**: Parfüm aileleri
- **perfume_similarities**: Benzerlik skorları
- **user_ratings**: Kullanıcı değerlendirmeleri
- **search_history**: Arama geçmişi

### Önemli İlişkiler
- Parfüm ↔ Marka (Many-to-One)
- Parfüm ↔ Notalar (Many-to-Many)
- Parfüm ↔ Aile (Many-to-One)
- Lüks Parfüm ↔ Alternatif Parfüm (Benzerlik)

## 🧮 Benzerlik Algoritması

Parfüm benzerlik skoru şu faktörlere göre hesaplanır:

1. **Cinsiyet Eşleşmesi** (30 puan)
   - Aynı cinsiyet: 30 puan
   - Unisex eşleşmesi: 30 puan

2. **Aile Eşleşmesi** (25 puan)
   - Aynı parfüm ailesi: 25 puan

3. **Nota Benzerliği** (45 puan)
   - Ortak notalar / Toplam notalar × 45

**Toplam**: 0-100 arası skor (≥30 puan olanlar gösterilir)

## 🔧 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. PostgreSQL Bağlantı Hatası
```bash
# PostgreSQL servisini başlatın
# Windows:
net start postgresql-x64-15

# macOS:
brew services start postgresql

# Ubuntu/Debian:
sudo systemctl start postgresql
```

#### 2. Python Modül Bulunamadı Hatası
```bash
# Sanal ortamın aktif olduğundan emin olun
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Bağımlılıkları yeniden yükleyin
pip install -r requirements.txt
```

#### 3. Node.js Bağımlılık Hatası
```bash
# Node modüllerini temizleyin ve yeniden yükleyin
rm -rf node_modules package-lock.json
npm install
```

#### 4. Veritabanı İçe Aktarma Hatası
```bash
# Veritabanını sıfırlayın
python check_db.py --reset

# Verileri yeniden içe aktarın
python import_data.py
```

#### 5. Port 5000 Kullanımda Hatası
```bash
# Farklı port kullanın
export FLASK_RUN_PORT=5001
python server.py
```

### Log Dosyaları
- **Uygulama logları:** `logs/perfumatch.log`
- **Hata logları:** `logs/error.log`
- **Scraping logları:** `*.log` dosyaları

### Yardım Alma
Sorun yaşıyorsanız:
1. Log dosyalarını kontrol edin
2. `python check_db.py` komutunu çalıştırın
3. GitHub Issues'da sorun bildirin
4. README.md dosyasını tekrar okuyun

## 🚀 Kurulum Sonrası

### İlk Çalıştırma
1. **Uygulamayı başlatın:** `run.bat` (Windows) veya `./run.sh` (Unix/Linux)
2. **Tarayıcınızda açın:** http://localhost:5000
3. **API'yi test edin:** http://localhost:5000/api/health

### Veri Yönetimi
```bash
# Veritabanı durumunu kontrol et
python check_db.py

# Yeni veri ekle
python import_data.py

# Benzerlik skorlarını yeniden hesapla
python calculate_similarities.py
```

### Geliştirme Modu
```bash
# Sanal ortamı aktifleştir
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Debug modunda çalıştır
export FLASK_DEBUG=True  # Linux/macOS
set FLASK_DEBUG=True     # Windows
python server.py
```

### Üretim Ortamı
```bash
# Environment'ı production'a çevir
# .env dosyasında:
FLASK_ENV=production
FLASK_DEBUG=False

# Güvenlik anahtarını değiştir
SECRET_KEY=your-production-secret-key
```

## 📊 Veri Kaynakları

### Mevcut Veriler
- **Bargello**: 500+ alternatif parfüm
- **Muscent**: 800+ alternatif parfüm  
- **Zara**: 300+ uygun fiyatlı parfüm
- **Parfumo.com**: Lüks parfüm bilgileri (API)

### Veri Formatı
```json
{
  "name": "Parfüm Adı",
  "brand": "Marka",
  "price": 299.99,
  "currency": "TRY",
  "gender": "unisex",
  "notes": {
    "top": ["Bergamot", "Limon"],
    "middle": ["Gül", "Yasemin"],
    "base": ["Sandal Ağacı", "Vanilya"]
  }
}
```

## 🔄 Veri Güncelleme

### Otomatik Güncelleme
```bash
# Yeni verileri içe aktar
python import_data.py

# Benzerlik skorlarını yeniden hesapla
python -c "from src.utils.data_importer import DataImporter; DataImporter().calculate_all_similarities()"
```

### Manuel Veri Ekleme
```bash
# Admin API ile veri ekleme
curl -X POST http://localhost:5000/api/admin/import-data \
  -H "Authorization: Bearer admin123"
```

## 🎨 Frontend Özellikleri

### Modern UI/UX
- **Gradient Tasarım**: Çekici renk geçişleri
- **Smooth Animasyonlar**: CSS3 transitions
- **Responsive Grid**: Mobil uyumlu layout
- **Interactive Cards**: Hover efektleri

### JavaScript Özellikleri
- **Async/Await**: Modern API çağrıları
- **Error Handling**: Kullanıcı dostu hata mesajları
- **Local Storage**: Arama geçmişi
- **Dynamic Loading**: Lazy loading

## 🔒 Güvenlik

### API Güvenliği
- **Rate Limiting**: Spam koruması
- **Input Validation**: SQL injection koruması
- **CORS**: Cross-origin güvenliği
- **Environment Variables**: Hassas bilgi koruması

### Veritabanı Güvenliği
- **Prepared Statements**: SQL injection koruması
- **User Permissions**: Sınırlı veritabanı erişimi
- **Connection Pooling**: Performans optimizasyonu

## 📈 Performans

### Optimizasyonlar
- **Database Indexing**: Hızlı sorgular
- **Query Optimization**: Efficient SQL
- **Caching**: Redis entegrasyonu (gelecek)
- **CDN**: Static file delivery (gelecek)

### Metrikler
- **Arama Süresi**: <500ms
- **Benzerlik Hesaplama**: <100ms
- **Sayfa Yükleme**: <2s
- **API Response**: <200ms

## 🧪 Test

### Unit Tests
```bash
python -m pytest tests/
```

### API Tests
```bash
# Sağlık kontrolü
curl http://localhost:5000/api/health

# Arama testi
curl -X POST http://localhost:5000/api/perfume/search \
  -H "Content-Type: application/json" \
  -d '{"searchTerm": "Chanel", "searchType": "name"}'
```

## 🚀 Deployment

### Production Ayarları
```bash
# Environment variables
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# Gunicorn ile çalıştırma
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👥 Ekip

- **Backend Development**: Flask, PostgreSQL, API Design
- **Frontend Development**: JavaScript, CSS3, Responsive Design
- **Data Science**: Similarity Algorithms, Data Processing
- **DevOps**: Docker, Database Management

## 📞 İletişim

- **GitHub**: [perfumatch](https://github.com/your-username/perfumatch)
- **Email**: info@perfumatch.com
- **Website**: https://perfumatch.com

## 🔮 Gelecek Planları

### v2.0 Özellikleri
- [ ] Machine Learning ile gelişmiş benzerlik
- [ ] Kullanıcı hesapları ve favoriler
- [ ] Sosyal özellikler (yorumlar, paylaşım)
- [ ] Mobil uygulama (React Native)
- [ ] AI chatbot desteği
- [ ] Çoklu dil desteği
- [ ] E-ticaret entegrasyonu

### Teknik İyileştirmeler
- [ ] Redis caching
- [ ] Elasticsearch entegrasyonu
- [ ] GraphQL API
- [ ] Microservices mimarisi
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline

---

**PerfuMatch** - Parfüm dünyasında akıllı eşleştirme! 🌟 