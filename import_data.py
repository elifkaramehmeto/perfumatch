#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PerfuMatch Veri İçe Aktarma Script'i
JSON dosyalarından PostgreSQL veritabanına veri aktarır
"""

import os
import sys
from flask import Flask
from src.models.database import init_db
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

def main():
    """Ana fonksiyon"""
    print("🎯 PerfuMatch Veri İçe Aktarma Başlatılıyor...")
    
    # Flask uygulamasını oluştur
    app = create_app()
    
    with app.app_context():
        try:
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
    success = main()
    sys.exit(0 if success else 1) 