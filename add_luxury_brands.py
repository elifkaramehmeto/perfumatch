#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lüks Parfüm Markalarını Ekleme Script'i
Bilinen pahalı markaları ve popüler parfümlerini veritabanına ekler
"""

import os
from decimal import Decimal
from flask import Flask
from src.models.database import init_db, db, Brand, Perfume, Note, PerfumeNote

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

def get_or_create_note(note_name: str, note_type: str = 'middle') -> Note:
    """Nota al veya oluştur"""
    note = Note.query.filter_by(name=note_name).first()
    if not note:
        # Nota kategorisini belirle
        category = determine_note_category(note_name)
        note = Note(name=note_name, type=note_type, category=category)
        db.session.add(note)
        db.session.flush()
    return note

def determine_note_category(note_name: str) -> str:
    """Nota kategorisini belirle"""
    note_name_lower = note_name.lower()
    
    categories = {
        'citrus': ['bergamot', 'lemon', 'orange', 'grapefruit', 'mandarin', 'lime', 'limon', 'portakal'],
        'floral': ['rose', 'jasmine', 'lavender', 'iris', 'neroli', 'gardenia', 'orchid', 'gül', 'yasemin'],
        'fruity': ['apple', 'peach', 'pear', 'pineapple', 'mango', 'strawberry', 'raspberry', 'elma', 'şeftali'],
        'spicy': ['pepper', 'cinnamon', 'clove', 'ginger', 'cardamom', 'saffron', 'biber', 'tarçın'],
        'woody': ['cedar', 'sandalwood', 'vetiver', 'patchouli', 'oud', 'sedir', 'sandal'],
        'sweet': ['vanilla', 'caramel', 'honey', 'sugar', 'vanilya', 'karamel'],
        'gourmand': ['coffee', 'chocolate', 'almond', 'kahve', 'çikolata'],
        'amber': ['amber', 'ambergris'],
        'musk': ['musk', 'misk'],
        'leather': ['leather', 'deri'],
        'tobacco': ['tobacco', 'tütün']
    }
    
    for category, keywords in categories.items():
        if any(keyword in note_name_lower for keyword in keywords):
            return category
    
    return 'other'

def add_perfume_notes(perfume, notes_data):
    """Parfüme notaları ekle"""
    for note_info in notes_data:
        if isinstance(note_info, str):
            note_name = note_info
            note_type = 'middle'
        else:
            note_name = note_info['name']
            note_type = note_info.get('type', 'middle')
        
        note = get_or_create_note(note_name, note_type)
        
        # Parfüm-nota ilişkisi zaten var mı kontrol et
        existing = PerfumeNote.query.filter_by(
            perfume_id=perfume.id,
            note_id=note.id
        ).first()
        
        if not existing:
            perfume_note = PerfumeNote(
                perfume_id=perfume.id,
                note_id=note.id
            )
            db.session.add(perfume_note)

def add_luxury_brands():
    """Lüks markaları ve parfümlerini ekle"""
    
    luxury_perfumes = [
        # CHANEL
        {
            'brand': 'Chanel',
            'name': 'Chanel No. 5',
            'gender': 'women',
            'price': Decimal('3500'),
            'notes': [
                {'name': 'Bergamot', 'type': 'top'},
                {'name': 'Lemon', 'type': 'top'},
                {'name': 'Neroli', 'type': 'top'},
                {'name': 'Jasmine', 'type': 'middle'},
                {'name': 'Rose', 'type': 'middle'},
                {'name': 'Lily of the Valley', 'type': 'middle'},
                {'name': 'Sandalwood', 'type': 'base'},
                {'name': 'Vanilla', 'type': 'base'},
                {'name': 'Amber', 'type': 'base'}
            ]
        },
        {
            'brand': 'Chanel',
            'name': 'Bleu de Chanel',
            'gender': 'men',
            'price': Decimal('3200'),
            'notes': [
                {'name': 'Grapefruit', 'type': 'top'},
                {'name': 'Lemon', 'type': 'top'},
                {'name': 'Mint', 'type': 'top'},
                {'name': 'Ginger', 'type': 'middle'},
                {'name': 'Nutmeg', 'type': 'middle'},
                {'name': 'Jasmine', 'type': 'middle'},
                {'name': 'Cedar', 'type': 'base'},
                {'name': 'Sandalwood', 'type': 'base'},
                {'name': 'Amber', 'type': 'base'}
            ]
        },
        
        # DIOR
        {
            'brand': 'Dior',
            'name': 'Sauvage',
            'gender': 'men',
            'price': Decimal('2800'),
            'notes': [
                {'name': 'Bergamot', 'type': 'top'},
                {'name': 'Pepper', 'type': 'top'},
                {'name': 'Lavender', 'type': 'middle'},
                {'name': 'Patchouli', 'type': 'middle'},
                {'name': 'Geranium', 'type': 'middle'},
                {'name': 'Vetiver', 'type': 'base'},
                {'name': 'Cedar', 'type': 'base'},
                {'name': 'Labdanum', 'type': 'base'}
            ]
        },
        {
            'brand': 'Dior',
            'name': 'Miss Dior',
            'gender': 'women',
            'price': Decimal('3000'),
            'notes': [
                {'name': 'Blood Orange', 'type': 'top'},
                {'name': 'Mandarin', 'type': 'top'},
                {'name': 'Rose', 'type': 'middle'},
                {'name': 'Peony', 'type': 'middle'},
                {'name': 'Lily of the Valley', 'type': 'middle'},
                {'name': 'Patchouli', 'type': 'base'},
                {'name': 'Musk', 'type': 'base'},
                {'name': 'Rosewood', 'type': 'base'}
            ]
        },
        
        # TOM FORD
        {
            'brand': 'Tom Ford',
            'name': 'Black Orchid',
            'gender': 'unisex',
            'price': Decimal('4500'),
            'notes': [
                {'name': 'Truffle', 'type': 'top'},
                {'name': 'Gardenia', 'type': 'top'},
                {'name': 'Black Currant', 'type': 'top'},
                {'name': 'Orchid', 'type': 'middle'},
                {'name': 'Spices', 'type': 'middle'},
                {'name': 'Lotus Wood', 'type': 'middle'},
                {'name': 'Vanilla', 'type': 'base'},
                {'name': 'Sandalwood', 'type': 'base'},
                {'name': 'Patchouli', 'type': 'base'}
            ]
        },
        {
            'brand': 'Tom Ford',
            'name': 'Oud Wood',
            'gender': 'unisex',
            'price': Decimal('5200'),
            'notes': [
                {'name': 'Oud', 'type': 'top'},
                {'name': 'Rosewood', 'type': 'top'},
                {'name': 'Cardamom', 'type': 'top'},
                {'name': 'Sandalwood', 'type': 'middle'},
                {'name': 'Palissander', 'type': 'middle'},
                {'name': 'Amber', 'type': 'base'},
                {'name': 'Vanilla', 'type': 'base'}
            ]
        },
        
        # CREED
        {
            'brand': 'Creed',
            'name': 'Aventus',
            'gender': 'men',
            'price': Decimal('6500'),
            'notes': [
                {'name': 'Pineapple', 'type': 'top'},
                {'name': 'Bergamot', 'type': 'top'},
                {'name': 'Black Currant', 'type': 'top'},
                {'name': 'Apple', 'type': 'top'},
                {'name': 'Birch', 'type': 'middle'},
                {'name': 'Patchouli', 'type': 'middle'},
                {'name': 'Moroccan Jasmine', 'type': 'middle'},
                {'name': 'Rose', 'type': 'middle'},
                {'name': 'Musk', 'type': 'base'},
                {'name': 'Oak Moss', 'type': 'base'},
                {'name': 'Ambergris', 'type': 'base'},
                {'name': 'Vanilla', 'type': 'base'}
            ]
        },
        
        # YVES SAINT LAURENT
        {
            'brand': 'Yves Saint Laurent',
            'name': 'Black Opium',
            'gender': 'women',
            'price': Decimal('2900'),
            'notes': [
                {'name': 'Pink Pepper', 'type': 'top'},
                {'name': 'Orange Blossom', 'type': 'top'},
                {'name': 'Pear', 'type': 'top'},
                {'name': 'Coffee', 'type': 'middle'},
                {'name': 'Jasmine', 'type': 'middle'},
                {'name': 'Bitter Almond', 'type': 'middle'},
                {'name': 'Vanilla', 'type': 'base'},
                {'name': 'Patchouli', 'type': 'base'},
                {'name': 'Cedar', 'type': 'base'}
            ]
        },
        
        # VERSACE
        {
            'brand': 'Versace',
            'name': 'Eros',
            'gender': 'men',
            'price': Decimal('2200'),
            'notes': [
                {'name': 'Mint', 'type': 'top'},
                {'name': 'Green Apple', 'type': 'top'},
                {'name': 'Lemon', 'type': 'top'},
                {'name': 'Tonka Bean', 'type': 'middle'},
                {'name': 'Geranium', 'type': 'middle'},
                {'name': 'Ambroxan', 'type': 'middle'},
                {'name': 'Vanilla', 'type': 'base'},
                {'name': 'Vetiver', 'type': 'base'},
                {'name': 'Oak Moss', 'type': 'base'}
            ]
        },
        
        # GIORGIO ARMANI
        {
            'brand': 'Giorgio Armani',
            'name': 'Acqua di Gio',
            'gender': 'men',
            'price': Decimal('2500'),
            'notes': [
                {'name': 'Lime', 'type': 'top'},
                {'name': 'Lemon', 'type': 'top'},
                {'name': 'Bergamot', 'type': 'top'},
                {'name': 'Jasmine', 'type': 'middle'},
                {'name': 'Calone', 'type': 'middle'},
                {'name': 'Freesia', 'type': 'middle'},
                {'name': 'White Musk', 'type': 'base'},
                {'name': 'Cedar', 'type': 'base'},
                {'name': 'Amber', 'type': 'base'}
            ]
        }
    ]
    
    print("🏆 Lüks markalar ekleniyor...")
    
    for perfume_data in luxury_perfumes:
        try:
            # Markayı al veya oluştur
            brand_name = perfume_data['brand']
            brand = Brand.query.filter_by(name=brand_name).first()
            if not brand:
                brand = Brand(name=brand_name, type='luxury')
                db.session.add(brand)
                db.session.flush()
            
            # Parfümün zaten var olup olmadığını kontrol et
            existing_perfume = Perfume.query.filter_by(
                name=perfume_data['name'],
                brand_id=brand.id
            ).first()
            
            if existing_perfume:
                print(f"⚠️  {perfume_data['name']} zaten mevcut, atlanıyor...")
                continue
            
            # Parfümü oluştur
            perfume = Perfume(
                name=perfume_data['name'],
                brand_id=brand.id,
                gender=perfume_data['gender'],
                price=perfume_data['price'],
                description=f"Lüks {brand_name} parfümü"
            )
            
            db.session.add(perfume)
            db.session.flush()
            
            # Notaları ekle
            add_perfume_notes(perfume, perfume_data['notes'])
            
            print(f"✅ {brand_name} - {perfume_data['name']} eklendi")
            
        except Exception as e:
            print(f"❌ Hata: {perfume_data['name']} - {e}")
            db.session.rollback()
            continue
    
    db.session.commit()
    print("🎉 Lüks markalar başarıyla eklendi!")

def main():
    """Ana fonksiyon"""
    print("🎯 Lüks Parfüm Markaları Ekleme Başlatılıyor...")
    
    app = create_app()
    
    with app.app_context():
        try:
            add_luxury_brands()
            
            # İstatistikleri göster
            luxury_brands = Brand.query.filter_by(type='luxury').count()
            luxury_perfumes = Perfume.query.join(Brand).filter(Brand.type == 'luxury').count()
            
            print(f"\n📊 Sonuç:")
            print(f"🏆 Lüks marka sayısı: {luxury_brands}")
            print(f"🧴 Lüks parfüm sayısı: {luxury_perfumes}")
            
            return True
            
        except Exception as e:
            print(f"❌ Genel hata: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = main()
    print(f"\n🏁 Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}") 