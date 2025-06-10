#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Full Import Script - Tüm parfüm verilerini import eder
"""

import os
import time
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
    """Veritabanını temizle"""
    print("🧹 Veritabanı temizleniyor...")
    
    try:
        # Benzerlik kayıtlarını sil
        deleted = PerfumeSimilarity.query.delete()
        print(f"✅ {deleted} benzerlik kaydı silindi")
        
        # Parfüm-nota ilişkilerini sil
        deleted = PerfumeNote.query.delete()
        print(f"✅ {deleted} parfüm-nota ilişkisi silindi")
        
        # Parfümleri sil
        deleted = Perfume.query.delete()
        print(f"✅ {deleted} parfüm silindi")
        
        # Notaları sil
        deleted = Note.query.delete()
        print(f"✅ {deleted} nota silindi")
        
        # Markaları sil (sadece alternative ve luxury olanları)
        deleted = Brand.query.filter(Brand.type.in_(['alternative', 'luxury'])).delete()
        print(f"✅ {deleted} marka silindi")
        
        db.session.commit()
        print("✅ Veritabanı temizleme tamamlandı")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı temizleme hatası: {e}")
        db.session.rollback()
        return False

def main():
    """Ana fonksiyon"""
    print("🎯 PerfuMatch Full Import Başlatılıyor...")
    
    # Flask uygulamasını oluştur
    app = create_app()
    
    with app.app_context():
        try:
            # Veritabanını temizle
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
                return False
            
            print("✅ Tüm JSON dosyaları mevcut")
            
            # Verileri sırayla import et
            print("\n🚀 Veri import işlemi başlıyor...")
            
            # 1. Bargello
            print("\n📦 Bargello verileri import ediliyor...")
            start_time = time.time()
            importer.import_bargello_data()
            print(f"✅ Bargello tamamlandı ({time.time() - start_time:.2f}s)")
            
            # Ara durum
            perfume_count = Perfume.query.count()
            note_count = Note.query.count()
            print(f"📊 Mevcut durum: {perfume_count} parfüm, {note_count} nota")
            
            # 2. Muscent
            print("\n📦 Muscent verileri import ediliyor...")
            start_time = time.time()
            importer.import_muscent_data()
            print(f"✅ Muscent tamamlandı ({time.time() - start_time:.2f}s)")
            
            # Ara durum
            perfume_count = Perfume.query.count()
            note_count = Note.query.count()
            print(f"📊 Mevcut durum: {perfume_count} parfüm, {note_count} nota")
            
            # 3. Zara
            print("\n📦 Zara verileri import ediliyor...")
            start_time = time.time()
            importer.import_zara_data()
            print(f"✅ Zara tamamlandı ({time.time() - start_time:.2f}s)")
            
            # Final durum
            perfume_count = Perfume.query.count()
            note_count = Note.query.count()
            brand_count = Brand.query.count()
            print(f"📊 Final durum: {perfume_count} parfüm, {note_count} nota, {brand_count} marka")
            
            # 4. Benzerlik hesaplama
            print("\n🔄 Benzerlik skorları hesaplanıyor...")
            start_time = time.time()
            importer.calculate_all_similarities()
            print(f"✅ Benzerlik hesaplama tamamlandı ({time.time() - start_time:.2f}s)")
            
            similarity_count = PerfumeSimilarity.query.count()
            print(f"📊 {similarity_count} benzerlik kaydı oluşturuldu")
            
            print("\n🎉 Tüm import işlemleri başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            print(f"❌ Import hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = main()
    print(f"\n🏁 Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}") 