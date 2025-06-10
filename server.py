#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Veritabanı modelleri
from src.models.database import (
    db, init_db, Brand, Perfume, PerfumeFamily, Note, PerfumeNote, 
    PerfumeSimilarity, UserRating, SearchHistory,
    search_perfumes_by_name, search_perfumes_by_notes, 
    search_perfumes_by_family, get_similar_perfumes
)

# Veri içe aktarma
from src.utils.data_importer import DataImporter

# Environment variables yükle
load_dotenv()

# Logging ayarları
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = Flask(__name__)
CORS(app)  # CORS'u etkinleştir

# Veritabanı konfigürasyonu
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://perfumatch_user:perfumatch_pass@localhost:5432/perfumatch_db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanını başlat
init_db(app)

# Statik dosyalar için route'lar
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/perfume-detail.html')
def serve_perfume_detail():
    return send_from_directory('.', 'perfume-detail.html')

@app.route('/src/<path:filename>')
def serve_src(filename):
    return send_from_directory('src', filename)

@app.route('/scrapping/<path:filename>')
def serve_scrapping(filename):
    return send_from_directory('scrapping', filename)

# API endpoint'leri

@app.route('/api/perfume/search', methods=['POST'])
def search_perfume():
    """Parfüm arama - veritabanından"""
    try:
        data = request.get_json()
        search_type = data.get('searchType', 'name')
        search_term = data.get('searchTerm', '').strip()
        gender = data.get('gender', 'all')
        limit = data.get('limit', 10)
        
        if not search_term:
            return jsonify({'error': 'Arama terimi gerekli'}), 400
        
        logging.info(f"Veritabanında arama: {search_type} - {search_term}")
        
        # Arama geçmişine kaydet
        save_search_history(search_term, search_type, request.remote_addr, request.user_agent.string)
        
        results = []
        
        if search_type == 'name':
            perfumes = search_perfumes_by_name(search_term, limit)
            results = [p.to_dict(include_similarities=True) for p in perfumes]
            
        elif search_type == 'notes':
            # Nota isimlerini ayır
            note_names = [n.strip() for n in search_term.split(',')]
            perfumes = search_perfumes_by_notes(note_names, limit)
            results = [p.to_dict() for p in perfumes]
            
        elif search_type == 'family':
            perfumes = search_perfumes_by_family(search_term, limit)
            results = [p.to_dict() for p in perfumes]
        
        # Cinsiyet filtreleme
        if gender != 'all':
            gender_map = {'men': 'men', 'women': 'women', 'unisex': 'unisex'}
            if gender in gender_map:
                results = [r for r in results if r['gender'] == gender_map[gender]]
        
        return jsonify({
            'results': results,
            'count': len(results),
            'search_type': search_type,
            'search_term': search_term
        })
        
    except Exception as e:
        logging.error(f"Arama API hatası: {e}")
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/perfume/parfumo-search', methods=['POST'])
def parfumo_search_perfume():
    """Parfumo.com'dan parfüm arama"""
    try:
        data = request.get_json()
        brand = data.get('brand', '').strip()
        perfume_name = data.get('perfumeName', '').strip()
        
        if not brand or not perfume_name:
            return jsonify({'error': 'Marka ve parfüm adı gerekli'}), 400
        
        logging.info(f"Parfumo'dan parfüm aranıyor: {brand} - {perfume_name}")
        
        # Python script'ini çağır
        result = call_python_scraper(brand, perfume_name)
        
        if result:
            # Veritabanından benzer parfümleri bul
            similar_perfumes = find_similar_perfumes_in_db(result.get('notes', []))
            result['database_alternatives'] = similar_perfumes
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Parfüm bilgileri bulunamadı'}), 404
            
    except Exception as e:
        logging.error(f"Parfumo API hatası: {e}")
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/perfume/<int:perfume_id>')
def get_perfume_detail(perfume_id):
    """Parfüm detayını getir"""
    try:
        perfume = Perfume.query.get_or_404(perfume_id)
        return jsonify(perfume.to_dict(include_notes=True, include_similarities=True))
    except Exception as e:
        logging.error(f"Parfüm detay hatası: {e}")
        return jsonify({'error': 'Parfüm bulunamadı'}), 404

@app.route('/api/perfume/<int:perfume_id>/alternatives')
def get_perfume_alternatives(perfume_id):
    """Parfümün alternatiflerini getir"""
    try:
        similarities = get_similar_perfumes(perfume_id, limit=10)
        results = [sim.to_dict() for sim in similarities]
        return jsonify({'alternatives': results})
    except Exception as e:
        logging.error(f"Alternatif getirme hatası: {e}")
        return jsonify({'error': 'Alternatifler bulunamadı'}), 404

@app.route('/api/brands')
def get_brands():
    """Tüm markaları getir"""
    try:
        brands = Brand.query.all()
        return jsonify([brand.to_dict() for brand in brands])
    except Exception as e:
        logging.error(f"Marka listesi hatası: {e}")
        return jsonify({'error': 'Markalar getirilemedi'}), 500

@app.route('/api/families')
def get_families():
    """Parfüm ailelerini getir"""
    try:
        families = PerfumeFamily.query.all()
        return jsonify([family.to_dict() for family in families])
    except Exception as e:
        logging.error(f"Aile listesi hatası: {e}")
        return jsonify({'error': 'Aileler getirilemedi'}), 500

@app.route('/api/notes')
def get_notes():
    """Notaları getir"""
    try:
        note_type = request.args.get('type')  # top, middle, base
        query = Note.query
        
        if note_type:
            query = query.filter_by(type=note_type)
        
        notes = query.all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        logging.error(f"Nota listesi hatası: {e}")
        return jsonify({'error': 'Notalar getirilemedi'}), 500

@app.route('/api/perfume/<int:perfume_id>/rate', methods=['POST'])
def rate_perfume(perfume_id):
    """Parfümü değerlendir"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')
        similarity_id = data.get('similarity_id')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Geçerli bir değerlendirme (1-5) gerekli'}), 400
        
        user_rating = UserRating(
            perfume_id=perfume_id,
            similarity_id=similarity_id,
            rating=rating,
            comment=comment,
            ip_address=request.remote_addr
        )
        
        db.session.add(user_rating)
        db.session.commit()
        
        return jsonify({'message': 'Değerlendirme kaydedildi', 'rating_id': user_rating.id})
        
    except Exception as e:
        logging.error(f"Değerlendirme hatası: {e}")
        db.session.rollback()
        return jsonify({'error': 'Değerlendirme kaydedilemedi'}), 500

@app.route('/api/popular-perfumes')
def get_popular_perfumes():
    """Popüler parfümleri getir"""
    try:
        # En çok aranan parfümler (arama geçmişinden)
        popular_searches = db.session.query(
            SearchHistory.search_term,
            db.func.count(SearchHistory.id).label('search_count')
        ).filter(
            SearchHistory.search_type == 'name'
        ).group_by(
            SearchHistory.search_term
        ).order_by(
            db.func.count(SearchHistory.id).desc()
        ).limit(10).all()
        
        # En yüksek puanlı parfümler
        top_rated = Perfume.query.filter(
            Perfume.rating.isnot(None)
        ).order_by(
            Perfume.rating.desc()
        ).limit(10).all()
        
        return jsonify({
            'popular_searches': [{'term': term, 'count': count} for term, count in popular_searches],
            'top_rated': [p.to_dict() for p in top_rated]
        })
        
    except Exception as e:
        logging.error(f"Popüler parfüm hatası: {e}")
        return jsonify({'error': 'Popüler parfümler getirilemedi'}), 500

@app.route('/api/admin/import-data', methods=['POST'])
def import_data():
    """Veri içe aktarma (Admin)"""
    try:
        # Basit güvenlik kontrolü
        auth_key = request.headers.get('Authorization')
        if auth_key != 'Bearer admin123':
            return jsonify({'error': 'Yetkisiz erişim'}), 401
        
        importer = DataImporter()
        importer.import_all_data()
        
        return jsonify({'message': 'Veriler başarıyla içe aktarıldı'})
        
    except Exception as e:
        logging.error(f"Veri içe aktarma hatası: {e}")
        return jsonify({'error': 'Veri içe aktarma başarısız'}), 500

@app.route('/api/health')
def health_check():
    """Sunucu sağlık kontrolü"""
    try:
        # Veritabanı bağlantısını test et
        db.session.execute(db.text('SELECT 1'))
        
        # İstatistikleri al
        perfume_count = Perfume.query.count()
        brand_count = Brand.query.count()
        similarity_count = PerfumeSimilarity.query.count()
        
        return jsonify({
            'status': 'healthy',
            'message': 'PerfuMatch API çalışıyor',
            'database': 'connected',
            'stats': {
                'perfumes': perfume_count,
                'brands': brand_count,
                'similarities': similarity_count
            }
        })
    except Exception as e:
        logging.error(f"Sağlık kontrolü hatası: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': 'Veritabanı bağlantı hatası',
            'error': str(e)
        }), 500

# Yardımcı fonksiyonlar

def call_python_scraper(brand, perfume_name):
    """Python scraper script'ini çağır"""
    try:
        script_path = Path('scrapping/request_branded.py')
        
        if not script_path.exists():
            logging.error(f"Script bulunamadı: {script_path}")
            return None
        
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        input_data = f"{brand}\n{perfume_name}\n"
        stdout, stderr = process.communicate(input=input_data, timeout=30)
        
        if process.returncode == 0 and stdout.strip():
            try:
                result = json.loads(stdout.strip())
                logging.info("Python script başarıyla çalıştı")
                return result
            except json.JSONDecodeError as e:
                logging.error(f"JSON parse hatası: {e}")
                return None
        else:
            logging.error(f"Script hatası: {stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logging.error("Script timeout")
        return None
    except Exception as e:
        logging.error(f"Script çağırma hatası: {e}")
        return None

def find_similar_perfumes_in_db(notes_list):
    """Veritabanında benzer parfümleri bul"""
    try:
        if not notes_list:
            return []
        
        # Nota isimlerini normalize et
        note_names = [note.strip() for note in notes_list if note.strip()]
        
        # Benzer parfümleri bul
        perfumes = search_perfumes_by_notes(note_names, limit=5)
        
        # Sadece alternatif markaları döndür
        alternative_brands = Brand.query.filter_by(type='alternative').all()
        alternative_brand_ids = [b.id for b in alternative_brands]
        
        alternatives = [
            p.to_dict() for p in perfumes 
            if p.brand_id in alternative_brand_ids
        ]
        
        return alternatives
        
    except Exception as e:
        logging.error(f"Benzer parfüm arama hatası: {e}")
        return []

def save_search_history(search_term, search_type, ip_address, user_agent):
    """Arama geçmişini kaydet"""
    try:
        search_history = SearchHistory(
            search_term=search_term,
            search_type=search_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(search_history)
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Arama geçmişi kaydetme hatası: {e}")
        db.session.rollback()

# Mock endpoint (test için)
@app.route('/api/perfume/mock/<brand>/<perfume_name>')
def get_mock_perfume(brand, perfume_name):
    """Test için mock data endpoint'i"""
    mock_data = {
        "url": f"https://www.parfumo.com/Perfumes/{brand}/{perfume_name}",
        "perfumer": "Test Parfümör",
        "notes": ["Bergamot", "Gül", "Sandal Ağacı", "Vanilya", "Misk"],
        "ratings": {
            "Scent": "8.5",
            "Longevity": "7.8",
            "Sillage": "8.0",
            "Bottle": "7.5"
        },
        "gender": "Unisex",
        "bargello_recommendations": [
            {
                "isim": f"{perfume_name} Muadili 1",
                "benzerlik": "94%",
                "notalar": {
                    "Üst Notalar": "Bergamot, Limon, Greyfurt",
                    "Orta Notalar": "Gül, Yasemin, Lavanta",
                    "Alt Notalar": "Sandal Ağacı, Vanilya, Misk"
                }
            }
        ]
    }
    
    return jsonify(mock_data)

# Hata yakalayıcıları
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    # Gerekli dosyaların varlığını kontrol et
    required_files = [
        'index.html',
        'perfume-detail.html',
        'bargello_parfumler.json',
        'scrapping/request_branded.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logging.warning(f"Eksik dosyalar: {missing_files}")
    
    # Sunucu bilgilerini yazdır
    logging.info("🎯 PerfuMatch sunucusu başlatılıyor...")
    logging.info("📝 Mevcut endpoint'ler:")
    logging.info("   - GET  /                          -> Ana sayfa")
    logging.info("   - GET  /perfume-detail.html       -> Parfüm detay sayfası")
    logging.info("   - POST /api/perfume/search        -> Veritabanı parfüm arama")
    logging.info("   - POST /api/perfume/parfumo-search -> Parfumo.com arama")
    logging.info("   - GET  /api/perfume/<id>          -> Parfüm detayı")
    logging.info("   - GET  /api/perfume/<id>/alternatives -> Parfüm alternatifleri")
    logging.info("   - GET  /api/brands                -> Marka listesi")
    logging.info("   - GET  /api/families              -> Parfüm aileleri")
    logging.info("   - GET  /api/notes                 -> Nota listesi")
    logging.info("   - GET  /api/popular-perfumes      -> Popüler parfümler")
    logging.info("   - POST /api/admin/import-data     -> Veri içe aktarma")
    logging.info("   - GET  /api/health                -> Sağlık kontrolü")
    
    # Sunucuyu başlat
    app.run(host='0.0.0.0', port=5000, debug=True) 