#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PerfuMatch Veri İçe Aktarma Script'i
JSON dosyalarından PostgreSQL veritabanına veri aktarır
"""

import os
import sys
from flask import Flask
from src.models.database import init_db, db, Perfume, PerfumeNote, Note, Brand, PerfumeSimilarity
from src.utils.data_importer import DataImporter

def create_app():
    """Flask uygulaması oluştur"""
    app = Flask(__name__)
    
    # Veritabanı konfigürasyonu
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://perfumatch_user:perfumatch_pass@localhost:5432/perfumatch_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Veritabanını başlat
    init_db(app)
    
    return app

def clean_database():
    """Veritabanını temizle (sadece import edilen veriler)"""
    print("🧹 Veritabanı temizleniyor...")
    
    try:
        # Benzerlik kayıtlarını sil
        PerfumeSimilarity.query.delete()
        print("✅ Benzerlik kayıtları silindi")
        
        # Parfüm-nota ilişkilerini sil
        PerfumeNote.query.delete()
        print("✅ Parfüm-nota ilişkileri silindi")
        
        # Parfümleri sil
        Perfume.query.delete()
        print("✅ Parfümler silindi")
        
        # Notaları sil
        Note.query.delete()
        print("✅ Notalar silindi")
        
        # Markaları sil (sadece alternative ve luxury olanları)
        Brand.query.filter(Brand.type.in_(['alternative', 'luxury'])).delete()
        print("✅ Markalar silindi")
        
        db.session.commit()
        print("✅ Veritabanı temizleme tamamlandı")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı temizleme hatası: {e}")
        db.session.rollback()
        return False

def main():
    """Ana fonksiyon"""
    print("🎯 PerfuMatch Veri İçe Aktarma Başlatılıyor...")
    
    # Komut satırı argümanlarını kontrol et
    clean_first = '--clean' in sys.argv or '-c' in sys.argv
    
    # Flask uygulamasını oluştur
    app = create_app()
    
    with app.app_context():
        try:
            # Temizleme seçeneği
            if clean_first:
                if not clean_database():
                    return False
            
            # Veri içe aktarıcıyı başlat
            importer = DataImporter()
            
            print("📊 JSON dosyaları kontrol ediliyor...")
            
            # Dosya varlığını kontrol et
            files_to_check = [
                'bargello_parfumler.json',
                'muscent_parfumler.json', 
                'zara_perfumes_20250610_005616.json'
            ]
            
            missing_files = []
            for file_path in files_to_check:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"❌ Eksik dosyalar: {missing_files}")
                print("Lütfen JSON dosyalarının proje dizininde olduğundan emin olun.")
                return False
            
            print("✅ Tüm JSON dosyaları mevcut")
            
            # Verileri içe aktar
            print("🚀 Veri içe aktarma başlıyor...")
            importer.import_all_data()
            
            print("✅ Veri içe aktarma başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            print(f"❌ Veri içe aktarma hatası: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Kullanım:")
        print("  python import_data.py           # Normal import")
        print("  python import_data.py --clean   # Önce veritabanını temizle, sonra import et")
        print("  python import_data.py -c        # Kısa versiyon")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1) 