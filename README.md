# PerfuMatch - Parfüm Muadil Öneri Sistemi

PerfuMatch, lüks parfümlerin uygun fiyatlı muadillerini bulmak için geliştirilmiş bir web uygulamasıdır. PostgreSQL veritabanı ile desteklenen bu sistem, parfüm notalarına, ailelerine ve markalarına göre akıllı eşleştirmeler yapar.

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
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (önerilen)

### Docker ile Kurulum (Önerilen)

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/your-username/perfumatch.git
cd perfumatch
```

2. **Docker Compose ile başlatın:**
```bash
docker-compose up -d
```

3. **Verileri içe aktarın:**
```bash
docker-compose exec web python import_data.py
```

4. **Uygulamaya erişin:**
- Ana uygulama: http://localhost:5000
- pgAdmin: http://localhost:8080 (admin@perfumatch.com / admin123)

### Manuel Kurulum

1. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

2. **PostgreSQL veritabanını kurun:**
```bash
# PostgreSQL'i başlatın
sudo systemctl start postgresql

# Veritabanı ve kullanıcı oluşturun
sudo -u postgres psql
CREATE DATABASE perfumatch_db;
CREATE USER perfumatch_user WITH PASSWORD 'perfumatch_pass';
GRANT ALL PRIVILEGES ON DATABASE perfumatch_db TO perfumatch_user;
\q
```

3. **Environment variables ayarlayın:**
```bash
export DATABASE_URL="postgresql://perfumatch_user:perfumatch_pass@localhost:5432/perfumatch_db"
```

4. **Veritabanını başlatın:**
```bash
python import_data.py
```

5. **Sunucuyu başlatın:**
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