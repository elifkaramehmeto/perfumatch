#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daha fazla test parfümü ekleme script'i
"""

import os
from flask import Flask
from src.models.database import init_db, db, Brand, Perfume, PerfumeFamily, Note, PerfumeNote
from datetime import datetime

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

def add_more_test_data():
    """Daha fazla test verisi ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            # Markalar
            brands_data = [
                {'name': 'Chanel', 'type': 'luxury'},
                {'name': 'Dior', 'type': 'luxury'},
                {'name': 'Tom Ford', 'type': 'luxury'},
                {'name': 'Bargello', 'type': 'alternative'},
                {'name': 'Golden Scent', 'type': 'alternative'}
            ]
            
            brands = {}
            for brand_data in brands_data:
                brand = Brand.query.filter_by(name=brand_data['name']).first()
                if not brand:
                    brand = Brand(**brand_data)
                    db.session.add(brand)
                brands[brand_data['name']] = brand
            
            # Parfüm aileleri
            families_data = [
                {'name': 'floral', 'description': 'Çiçeksi parfümler'},
                {'name': 'oriental', 'description': 'Oriental parfümler'},
                {'name': 'fresh', 'description': 'Taze parfümler'},
                {'name': 'fruity', 'description': 'Meyveli parfümler'}
            ]
            
            families = {}
            for family_data in families_data:
                family = PerfumeFamily.query.filter_by(name=family_data['name']).first()
                if not family:
                    family = PerfumeFamily(**family_data)
                    db.session.add(family)
                families[family_data['name']] = family
            
            # Woody ailesini de ekle
            woody_family = PerfumeFamily.query.filter_by(name='woody').first()
            if woody_family:
                families['woody'] = woody_family
            
            # Notalar
            notes_data = [
                {'name': 'Jasmine', 'type': 'middle', 'category': 'floral'},
                {'name': 'Vanilla', 'type': 'base', 'category': 'sweet'},
                {'name': 'Lemon', 'type': 'top', 'category': 'citrus'},
                {'name': 'Patchouli', 'type': 'base', 'category': 'woody'},
                {'name': 'Lavender', 'type': 'middle', 'category': 'herbal'},
                {'name': 'Amber', 'type': 'base', 'category': 'amber'},
                {'name': 'Apple', 'type': 'top', 'category': 'fruity'},
                {'name': 'Musk', 'type': 'base', 'category': 'animalic'}
            ]
            
            notes = {}
            for note_data in notes_data:
                note = Note.query.filter_by(name=note_data['name']).first()
                if not note:
                    note = Note(**note_data)
                    db.session.add(note)
                notes[note_data['name']] = note
            
            db.session.commit()
            
            # Parfümler
            perfumes_data = [
                {
                    'name': 'Chanel No.5',
                    'brand': 'Chanel',
                    'family': 'floral',
                    'gender': 'women',
                    'price': 2850.0,
                    'description': 'Klasik çiçeksi parfüm',
                    'notes': ['Bergamot', 'Jasmine', 'Sandalwood']
                },
                {
                    'name': 'Dior Sauvage',
                    'brand': 'Dior',
                    'family': 'fresh',
                    'gender': 'men',
                    'price': 2650.0,
                    'description': 'Taze ve maskülen',
                    'notes': ['Bergamot', 'Lavender', 'Amber']
                },
                {
                    'name': 'Tom Ford Oud Wood',
                    'brand': 'Tom Ford',
                    'family': 'woody',
                    'gender': 'unisex',
                    'price': 4250.0,
                    'description': 'Lüks odunsu parfüm',
                    'notes': ['Sandalwood', 'Patchouli', 'Vanilla']
                },
                {
                    'name': 'Bargello Classic',
                    'brand': 'Bargello',
                    'family': 'floral',
                    'gender': 'women',
                    'price': 385.0,
                    'description': 'Uygun fiyatlı çiçeksi alternatif',
                    'notes': ['Lemon', 'Rose', 'Musk']
                },
                {
                    'name': 'Golden Fresh',
                    'brand': 'Golden Scent',
                    'family': 'fresh',
                    'gender': 'men',
                    'price': 295.0,
                    'description': 'Taze erkek parfümü',
                    'notes': ['Apple', 'Lavender', 'Amber']
                }
            ]
            
            for perfume_data in perfumes_data:
                existing = Perfume.query.filter_by(name=perfume_data['name']).first()
                if not existing:
                    perfume = Perfume(
                        name=perfume_data['name'],
                        brand_id=brands[perfume_data['brand']].id,
                        family_id=families[perfume_data['family']].id,
                        gender=perfume_data['gender'],
                        price=perfume_data['price'],
                        currency='TRY',
                        description=perfume_data['description']
                    )
                    db.session.add(perfume)
                    db.session.commit()
                    
                    # Notaları ekle
                    for note_name in perfume_data['notes']:
                        if note_name in notes:
                            perfume_note = PerfumeNote(
                                perfume_id=perfume.id,
                                note_id=notes[note_name].id,
                                intensity=5
                            )
                            db.session.add(perfume_note)
                    
                    print(f"✅ {perfume_data['name']} eklendi")
            
            db.session.commit()
            print("🎯 Tüm test verileri başarıyla eklendi!")
            return True
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    add_more_test_data() 