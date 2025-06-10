#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.models.database import *
from server import app

def check_database():
    """Veritabanını kontrol et"""
    
    with app.app_context():
        print("🔍 Veritabanı kontrol ediliyor...")
        
        # Parfüm sayısı
        perfume_count = Perfume.query.count()
        print(f"📊 Toplam parfüm sayısı: {perfume_count}")
        
        # İlk 5 parfüm
        perfumes = Perfume.query.limit(5).all()
        print("\n📋 İlk 5 parfüm:")
        for p in perfumes:
            brand_name = p.brand.name if p.brand else "N/A"
            price_info = f"{p.price} TL" if p.price else "Fiyat yok"
            print(f"   ID: {p.id}, İsim: {p.name}, Marka: {brand_name}, Fiyat: {price_info}")
        
        # Fiyatlı parfümler
        priced_perfumes = Perfume.query.filter(Perfume.price.isnot(None)).limit(10).all()
        print(f"\n💰 Fiyatlı parfüm sayısı: {Perfume.query.filter(Perfume.price.isnot(None)).count()}")
        print("\n📋 İlk 10 fiyatlı parfüm:")
        for p in priced_perfumes:
            brand_name = p.brand.name if p.brand else "N/A"
            print(f"   {p.name[:50]}... - {brand_name}: {p.price} TL")
        
        # Benzerlik sayısı
        similarity_count = PerfumeSimilarity.query.count()
        print(f"\n🔗 Toplam benzerlik kaydı: {similarity_count}")
        
        # İlk 3 benzerlik
        similarities = PerfumeSimilarity.query.limit(3).all()
        print("\n📋 İlk 3 benzerlik:")
        for s in similarities:
            luxury_name = s.luxury_perfume.name if s.luxury_perfume else "N/A"
            alt_name = s.alternative_perfume.name if s.alternative_perfume else "N/A"
            print(f"   Lüks: {luxury_name} -> Alternatif: {alt_name} (Skor: {s.similarity_score}%)")
        
        # Lüks parfümler
        luxury_brands = Brand.query.filter_by(type='luxury').all()
        print(f"\n👑 Lüks marka sayısı: {len(luxury_brands)}")
        for brand in luxury_brands:
            perfume_count = Perfume.query.filter_by(brand_id=brand.id).count()
            print(f"   {brand.name}: {perfume_count} parfüm")

if __name__ == "__main__":
    check_database() 