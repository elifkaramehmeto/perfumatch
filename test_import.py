#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Import Script - Sadece Bargello verilerini import eder
"""

import os
from flask import Flask
from src.models.database import init_db, db
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
    print("🎯 Bargello Test Import Başlatılıyor...")
    
    # Flask uygulamasını oluştur
    app = create_app()
    
    with app.app_context():
        try:
            # Veri içe aktarıcıyı başlat
            importer = DataImporter()
            
            # Sadece Bargello verilerini import et
            print("🚀 Bargello verileri import ediliyor...")
            importer.import_bargello_data()
            
            print("✅ Bargello import tamamlandı!")
            return True
            
        except Exception as e:
            print(f"❌ Import hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = main()
    print(f"Sonuç: {'Başarılı' if success else 'Başarısız'}") 