#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test parfümü ekleme script'i
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

def add_test_data():
    """Test verisi ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test markası ekle
            brand = Brand.query.filter_by(name='Test Brand').first()
            if not brand:
                brand = Brand(name='Test Brand', type='alternative')
                db.session.add(brand)
                db.session.commit()
                print("✅ Test markası eklendi")
            
            # Test parfüm ailesi ekle
            family = PerfumeFamily.query.filter_by(name='woody').first()
            if not family:
                family = PerfumeFamily(name='woody', description='Odunsu parfümler')
                db.session.add(family)
                db.session.commit()
                print("✅ Woody aile eklendi")
            
            # Test notaları ekle
            notes_data = [
                {'name': 'Bergamot', 'type': 'top', 'category': 'citrus'},
                {'name': 'Sandalwood', 'type': 'base', 'category': 'woody'},
                {'name': 'Rose', 'type': 'middle', 'category': 'floral'}
            ]
            
            notes = []
            for note_data in notes_data:
                note = Note.query.filter_by(name=note_data['name']).first()
                if not note:
                    note = Note(**note_data)
                    db.session.add(note)
                notes.append(note)
            
            db.session.commit()
            print("✅ Test notaları eklendi")
            
            # Test parfümü ekle
            perfume = Perfume.query.filter_by(name='Test Woody Perfume').first()
            if not perfume:
                perfume = Perfume(
                    name='Test Woody Perfume',
                    brand_id=brand.id,
                    family_id=family.id,
                    gender='unisex',
                    price=150.0,
                    currency='TRY',
                    description='Test amaçlı odunsu parfüm'
                )
                db.session.add(perfume)
                db.session.commit()
                
                # Parfüm notalarını ekle
                for note in notes:
                    perfume_note = PerfumeNote(
                        perfume_id=perfume.id,
                        note_id=note.id,
                        intensity=5
                    )
                    db.session.add(perfume_note)
                
                db.session.commit()
                print("✅ Test parfümü eklendi")
            
            print("🎯 Test verisi başarıyla eklendi!")
            return True
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    add_test_data() 