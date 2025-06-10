#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Benzerlik Hesaplama Script'i
Lüks parfümler ile alternatif parfümler arasında benzerlik skorlarını hesaplar
"""

import os
from flask import Flask
from src.models.database import init_db, db, Brand, Perfume, PerfumeSimilarity
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
    print("🎯 Benzerlik Hesaplama Başlatılıyor...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Mevcut benzerlik kayıtlarını sil
            print("🧹 Eski benzerlik kayıtları temizleniyor...")
            deleted = PerfumeSimilarity.query.delete()
            print(f"✅ {deleted} eski kayıt silindi")
            db.session.commit()
            
            # Veri içe aktarıcıyı başlat
            importer = DataImporter()
            
            # Benzerlik hesaplama
            print("🔄 Benzerlik skorları hesaplanıyor...")
            importer.calculate_all_similarities()
            
            # Sonuçları göster
            similarity_count = PerfumeSimilarity.query.count()
            luxury_count = Perfume.query.join(Brand).filter(Brand.type == 'luxury').count()
            alternative_count = Perfume.query.join(Brand).filter(Brand.type == 'alternative').count()
            
            print(f"\n📊 Sonuç:")
            print(f"🏆 Lüks parfüm sayısı: {luxury_count}")
            print(f"🧴 Alternatif parfüm sayısı: {alternative_count}")
            print(f"🔗 Benzerlik kaydı sayısı: {similarity_count}")
            
            # En yüksek benzerlik skorlarını göster
            top_similarities = PerfumeSimilarity.query.order_by(
                PerfumeSimilarity.similarity_score.desc()
            ).limit(5).all()
            
            if top_similarities:
                print(f"\n🏅 En yüksek benzerlik skorları:")
                for sim in top_similarities:
                    luxury_perfume = Perfume.query.get(sim.luxury_perfume_id)
                    alternative_perfume = Perfume.query.get(sim.alternative_perfume_id)
                    luxury_brand = Brand.query.get(luxury_perfume.brand_id)
                    alternative_brand = Brand.query.get(alternative_perfume.brand_id)
                    
                    print(f"  📍 {luxury_brand.name} {luxury_perfume.name} ↔️ {alternative_brand.name} {alternative_perfume.name}")
                    price_diff = sim.price_difference if sim.price_difference else 0
                    print(f"     Benzerlik: %{sim.similarity_score:.1f} | Fiyat farkı: {price_diff:.0f}₺")
            
            return True
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = main()
    print(f"\n🏁 Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}") 