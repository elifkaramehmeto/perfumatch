#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from src.models.database import (
    db, Brand, Perfume, PerfumeFamily, Note, PerfumeNote, PerfumeSimilarity,
    calculate_similarity_score
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self):
        self.note_cache = {}
        self.brand_cache = {}
        self.family_cache = {}
        self.perfume_note_cache = set()  # Parfüm-nota kombinasyonlarını takip et
        
    def load_json_file(self, file_path: str) -> List[Dict]:
        """JSON dosyasını yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"JSON dosyası yüklenemedi {file_path}: {e}")
            return []
    
    def get_or_create_brand(self, brand_name: str, brand_type: str = 'alternative') -> Brand:
        """Marka al veya oluştur"""
        if brand_name in self.brand_cache:
            return self.brand_cache[brand_name]
        
        brand = Brand.query.filter_by(name=brand_name).first()
        if not brand:
            brand = Brand(name=brand_name, type=brand_type)
            db.session.add(brand)
            db.session.flush()
        
        self.brand_cache[brand_name] = brand
        return brand
    
    def get_or_create_family(self, family_name: str) -> Optional[PerfumeFamily]:
        """Parfüm ailesi al veya oluştur"""
        if not family_name:
            return None
            
        if family_name in self.family_cache:
            return self.family_cache[family_name]
        
        # Aile adını normalize et
        family_mapping = {
            'floral': 'Floral',
            'woody': 'Woody',
            'oriental': 'Oriental',
            'fresh': 'Fresh',
            'fruity': 'Fruity',
            'gourmand': 'Gourmand',
            'chypre': 'Chypre',
            'fougere': 'Fougere'
        }
        
        normalized_name = family_mapping.get(family_name.lower(), family_name.title())
        
        family = PerfumeFamily.query.filter_by(name=normalized_name).first()
        if not family:
            family = PerfumeFamily(name=normalized_name)
            db.session.add(family)
            db.session.flush()
        
        self.family_cache[family_name] = family
        return family
    
    def get_or_create_note(self, note_name: str, note_type: str = 'middle') -> Note:
        """Nota al veya oluştur - cache ve unique constraint hatalarını önle"""
        # Cache key'i sadece nota ismi olsun (type'a göre değil)
        if note_name in self.note_cache:
            return self.note_cache[note_name]
        
        # Önce veritabanında var mı kontrol et (isim bazında)
        note = Note.query.filter_by(name=note_name).first()
        if not note:
            # Nota kategorisini belirle
            category = self.determine_note_category(note_name)
            note = Note(name=note_name, type=note_type, category=category)
            try:
                db.session.add(note)
                db.session.flush()
            except Exception as e:
                # Unique constraint hatası durumunda tekrar sorgula
                db.session.rollback()
                note = Note.query.filter_by(name=note_name).first()
                if not note:
                    logger.error(f"Nota oluşturulamadı: {note_name}, Hata: {e}")
                    raise
        
        self.note_cache[note_name] = note
        return note
    
    def determine_note_category(self, note_name: str) -> str:
        """Nota kategorisini belirle"""
        note_name_lower = note_name.lower()
        
        # Kategori eşleştirmeleri
        categories = {
            'citrus': ['bergamot', 'limon', 'portakal', 'greyfurt', 'mandalina', 'lime'],
            'floral': ['gül', 'yasemin', 'lavanta', 'süsen', 'portakal çiçeği', 'neroli', 'gardenya', 'orkide'],
            'fruity': ['elma', 'şeftali', 'armut', 'ananas', 'mango', 'çilek', 'ahududu'],
            'spicy': ['biber', 'tarçın', 'karanfil', 'zencefil', 'kakule', 'safran'],
            'woody': ['sedir', 'sandal ağacı', 'vetiver', 'paçuli', 'oud'],
            'sweet': ['vanilya', 'karamel', 'bal', 'şeker'],
            'gourmand': ['kahve', 'çikolata', 'badem'],
            'amber': ['amber', 'kehribar'],
            'musk': ['misk'],
            'leather': ['deri'],
            'tobacco': ['tütün']
        }
        
        for category, keywords in categories.items():
            if any(keyword in note_name_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def parse_price(self, price_str: str) -> Tuple[Optional[Decimal], str]:
        """Fiyat string'ini parse et"""
        if not price_str:
            return None, 'TRY'
        
        # Boşlukları temizle
        price_str = price_str.replace(' ', '')
        
        # TL, ₺ veya TRY içeren fiyatları bul
        if '₺' in price_str or 'TL' in price_str or 'TRY' in price_str:
            currency = 'TRY'
            # Türkçe format: virgül decimal separator olarak kullanılır
            # Örnek: 320,00₺ -> 320.00
            price_str = price_str.replace('₺', '').replace('TL', '').replace('TRY', '')
            
            # Fiyat aralığı varsa ilk fiyatı al (örn: "320,00₺ – 690,00₺")
            if '–' in price_str or '-' in price_str:
                price_str = price_str.split('–')[0].split('-')[0].strip()
            
            # Virgülü noktaya çevir (Türkçe decimal format)
            price_str = price_str.replace(',', '.')
            
            # Sayısal değeri çıkar
            numbers = re.findall(r'\d+\.?\d*', price_str)
            if numbers:
                return Decimal(numbers[0]), currency
        
        # Diğer para birimleri için
        if '$' in price_str:
            currency = 'USD'
            price_str = price_str.replace('$', '')
        elif '€' in price_str:
            currency = 'EUR'
            price_str = price_str.replace('€', '')
        else:
            currency = 'TRY'
        
        # Fiyat aralığı varsa ilk fiyatı al
        if '–' in price_str or '-' in price_str:
            price_str = price_str.split('–')[0].split('-')[0].strip()
        
        # Nokta decimal separator olarak kullanılır (USD, EUR için)
        numbers = re.findall(r'\d+\.?\d*', price_str)
        if numbers:
            return Decimal(numbers[0]), currency
        
        return None, currency
    
    def determine_gender(self, perfume_data: Dict) -> str:
        """Parfümün cinsiyetini belirle"""
        # Önce açık cinsiyet bilgisini kontrol et
        if 'cinsiyet' in perfume_data.get('notalar', {}):
            gender = perfume_data['notalar']['cinsiyet'].lower()
            if 'erkek' in gender:
                return 'men'
            elif 'kadın' in gender:
                return 'women'
            elif 'unisex' in gender:
                return 'unisex'
        
        # İsimden çıkarım yap
        name = perfume_data.get('isim', '').lower()
        if 'erkek' in name or 'men' in name:
            return 'men'
        elif 'kadın' in name or 'women' in name or 'femme' in name:
            return 'women'
        elif 'unisex' in name:
            return 'unisex'
        
        # Etiketlerden çıkarım yap
        tags = perfume_data.get('etiketler', [])
        if isinstance(tags, list):
            for tag in tags:
                if tag.lower() in ['erkek', 'men']:
                    return 'men'
                elif tag.lower() in ['kadın', 'women', 'femme']:
                    return 'women'
                elif tag.lower() == 'unisex':
                    return 'unisex'
        
        return 'unisex'  # Varsayılan
    
    def parse_notes_from_bargello(self, notalar: Dict) -> List[Tuple[str, str]]:
        """Bargello notalarını parse et"""
        notes = []
        
        note_mapping = {
            'üst_notlar': 'top',
            'orta_notlar': 'middle', 
            'alt_notlar': 'base'
        }
        
        for key, note_type in note_mapping.items():
            if key in notalar and notalar[key] != "Yok":
                note_str = notalar[key]
                if isinstance(note_str, str):
                    # Virgülle ayrılmış notaları ayır
                    note_names = [n.strip() for n in note_str.split(',')]
                    for note_name in note_names:
                        if note_name:
                            notes.append((note_name, note_type))
        
        return notes
    
    def parse_notes_from_muscent(self, perfume_data: Dict) -> List[Tuple[str, str]]:
        """Muscent notalarını parse et"""
        notes = []
        
        # Notalar alanını kontrol et
        if 'notalar' in perfume_data:
            notalar = perfume_data['notalar']
            
            # En yoğun notalar
            if 'en_yogun_notalar' in notalar and notalar['en_yogun_notalar']:
                note_str = notalar['en_yogun_notalar']
                note_names = [n.strip() for n in note_str.split(',')]
                for note_name in note_names:
                    if note_name:
                        notes.append((note_name, 'middle'))
        
        # Etiketlerden de nota çıkar (cinsiyet etiketlerini hariç tut)
        if 'etiketler' in perfume_data:
            etiketler = perfume_data['etiketler']
            if isinstance(etiketler, list):
                gender_tags = ['erkek', 'kadın', 'unisex', 'men', 'women']
                for etiket in etiketler:
                    if etiket.lower() not in gender_tags:
                        notes.append((etiket.title(), 'middle'))
        
        return notes
    
    def parse_notes_from_zara(self, perfume_data: Dict) -> List[Tuple[str, str]]:
        """Zara notalarını parse et"""
        notes = []
        
        # Zara için genellikle description'dan nota çıkarımı yapılır
        # Şimdilik boş döndür, gerekirse daha sonra implement edilir
        
        return notes
    
    def add_perfume_note_safely(self, perfume_id: int, note_id: int) -> bool:
        """Parfüm-nota ilişkisini güvenli şekilde ekle"""
        # Cache'de var mı kontrol et
        cache_key = (perfume_id, note_id)
        if cache_key in self.perfume_note_cache:
            return False
        
        # Veritabanında var mı kontrol et
        existing = PerfumeNote.query.filter_by(
            perfume_id=perfume_id,
            note_id=note_id
        ).first()
        
        if existing:
            self.perfume_note_cache.add(cache_key)
            return False
        
        try:
            perfume_note = PerfumeNote(
                perfume_id=perfume_id,
                note_id=note_id
            )
            db.session.add(perfume_note)
            self.perfume_note_cache.add(cache_key)
            return True
        except Exception as e:
            logger.error(f"Parfüm-nota ilişkisi eklenemedi: {perfume_id}-{note_id}, Hata: {e}")
            db.session.rollback()
            return False
    
    def import_bargello_data(self, file_path: str = 'bargello_parfumler.json'):
        """Bargello verilerini içe aktar"""
        logger.info("Bargello verileri içe aktarılıyor...")
        
        data = self.load_json_file(file_path)
        if not data:
            return
        
        brand = self.get_or_create_brand('Bargello', 'alternative')
        imported_count = 0
        
        for item in data:
            try:
                # Parfümün zaten var olup olmadığını kontrol et
                existing = Perfume.query.filter_by(
                    name=item['isim'],
                    brand_id=brand.id
                ).first()
                
                if existing:
                    continue
                
                # Fiyat parse et
                price = None
                if 'fiyat' in item:
                    price, currency = self.parse_price(item['fiyat'])
                
                # Cinsiyet belirle
                gender = self.determine_gender(item)
                
                # Parfüm oluştur
                perfume = Perfume(
                    name=item['isim'],
                    brand_id=brand.id,
                    gender=gender,
                    price=price,
                    product_url=item.get('link'),
                    stock_status=item.get('stok_durumu') == 'Stokta var',
                    description=item.get('aciklama', '')
                )
                
                db.session.add(perfume)
                db.session.flush()
                
                # Notaları ekle
                if 'notalar' in item:
                    notes = self.parse_notes_from_bargello(item['notalar'])
                    for note_name, note_type in notes:
                        note = self.get_or_create_note(note_name, note_type)
                        self.add_perfume_note_safely(perfume.id, note.id)
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    db.session.commit()
                    logger.info(f"Bargello: {imported_count} parfüm içe aktarıldı")
                    
            except Exception as e:
                logger.error(f"Bargello parfüm içe aktarma hatası: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"Bargello içe aktarma tamamlandı: {imported_count} parfüm")
    
    def import_muscent_data(self, file_path: str = 'muscent_parfumler.json'):
        """Muscent verilerini içe aktar"""
        logger.info("Muscent verileri içe aktarılıyor...")
        
        data = self.load_json_file(file_path)
        if not data:
            return
        
        brand = self.get_or_create_brand('Muscent', 'alternative')
        imported_count = 0
        
        for item in data:
            try:
                # Parfümün zaten var olup olmadığını kontrol et
                existing = Perfume.query.filter_by(
                    name=item['isim'],
                    brand_id=brand.id
                ).first()
                
                if existing:
                    continue
                
                # Fiyat parse et
                price = None
                if 'fiyat' in item:
                    price, currency = self.parse_price(item['fiyat'])
                
                # Cinsiyet belirle
                gender = self.determine_gender(item)
                
                # Rating parse et
                rating = None
                if 'puan' in item and item['puan']:
                    try:
                        rating = Decimal(str(item['puan']))
                    except:
                        pass
                
                # Parfüm oluştur
                perfume = Perfume(
                    name=item['isim'],
                    brand_id=brand.id,
                    gender=gender,
                    price=price,
                    product_url=item.get('link'),
                    stock_status=item.get('stok_durumu', True),
                    rating=rating,
                    description=item.get('aciklama', '')
                )
                
                db.session.add(perfume)
                db.session.flush()
                
                # Notaları ekle
                notes = self.parse_notes_from_muscent(item)
                for note_name, note_type in notes:
                    note = self.get_or_create_note(note_name, note_type)
                    self.add_perfume_note_safely(perfume.id, note.id)
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    db.session.commit()
                    logger.info(f"Muscent: {imported_count} parfüm içe aktarıldı")
                    
            except Exception as e:
                logger.error(f"Muscent parfüm içe aktarma hatası: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"Muscent içe aktarma tamamlandı: {imported_count} parfüm")
    
    def import_zara_data(self, file_path: str = 'zara_perfumes_20250610_005616.json'):
        """Zara verilerini içe aktar"""
        logger.info("Zara verileri içe aktarılıyor...")
        
        data = self.load_json_file(file_path)
        if not data:
            return
        
        brand = self.get_or_create_brand('Zara', 'alternative')
        imported_count = 0
        
        for item in data:
            try:
                # Parfümün zaten var olup olmadığını kontrol et
                existing = Perfume.query.filter_by(
                    name=item['name'],
                    brand_id=brand.id
                ).first()
                
                if existing:
                    continue
                
                # Fiyat parse et
                price = None
                if 'price' in item:
                    price, currency = self.parse_price(item['price'])
                
                # Cinsiyet belirle (Zara için çoğunlukla unisex)
                gender = 'unisex'
                name_lower = item['name'].lower()
                if 'men' in name_lower or 'erkek' in name_lower:
                    gender = 'men'
                elif 'women' in name_lower or 'kadın' in name_lower:
                    gender = 'women'
                
                # Parfüm oluştur
                perfume = Perfume(
                    name=item['name'],
                    brand_id=brand.id,
                    gender=gender,
                    price=price,
                    product_url=item.get('product_url'),
                    image_url=item.get('image_url'),
                    description=item.get('description', ''),
                    stock_status=True
                )
                
                db.session.add(perfume)
                db.session.flush()
                
                # Notaları ekle
                notes = self.parse_notes_from_zara(item)
                for note_name, note_type in notes:
                    note = self.get_or_create_note(note_name, note_type)
                    self.add_perfume_note_safely(perfume.id, note.id)
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    db.session.commit()
                    logger.info(f"Zara: {imported_count} parfüm içe aktarıldı")
                    
            except Exception as e:
                logger.error(f"Zara parfüm içe aktarma hatası: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"Zara içe aktarma tamamlandı: {imported_count} parfüm")
    
    def calculate_all_similarities(self):
        """Tüm parfümler için benzerlik skorlarını hesapla"""
        logger.info("Benzerlik skorları hesaplanıyor...")
        
        # Lüks markaları al
        luxury_brands = Brand.query.filter_by(type='luxury').all()
        luxury_brand_ids = [b.id for b in luxury_brands]
        
        # Alternatif markaları al
        alternative_brands = Brand.query.filter_by(type='alternative').all()
        alternative_brand_ids = [b.id for b in alternative_brands]
        
        # Lüks parfümleri al
        luxury_perfumes = Perfume.query.filter(Perfume.brand_id.in_(luxury_brand_ids)).all()
        
        # Alternatif parfümleri al
        alternative_perfumes = Perfume.query.filter(Perfume.brand_id.in_(alternative_brand_ids)).all()
        
        similarity_count = 0
        
        for luxury_perfume in luxury_perfumes:
            for alternative_perfume in alternative_perfumes:
                # Zaten var olan benzerlik kaydını kontrol et
                existing = PerfumeSimilarity.query.filter_by(
                    luxury_perfume_id=luxury_perfume.id,
                    alternative_perfume_id=alternative_perfume.id
                ).first()
                
                if existing:
                    continue
                
                # Benzerlik skorunu hesapla
                score = calculate_similarity_score(luxury_perfume, alternative_perfume)
                
                # Sadece yeterince benzer olanları kaydet (>= 30 puan)
                if score >= 30:
                    # Fiyat farkını hesapla
                    price_diff = None
                    if luxury_perfume.price and alternative_perfume.price:
                        price_diff = luxury_perfume.price - alternative_perfume.price
                    
                    similarity = PerfumeSimilarity(
                        luxury_perfume_id=luxury_perfume.id,
                        alternative_perfume_id=alternative_perfume.id,
                        similarity_score=Decimal(str(score)),
                        gender_match=(luxury_perfume.gender == alternative_perfume.gender),
                        price_difference=price_diff
                    )
                    
                    db.session.add(similarity)
                    similarity_count += 1
                    
                    if similarity_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"{similarity_count} benzerlik kaydı oluşturuldu")
        
        db.session.commit()
        logger.info(f"Benzerlik hesaplama tamamlandı: {similarity_count} kayıt")
    
    def import_all_data(self):
        """Tüm verileri içe aktar"""
        logger.info("Tüm veriler içe aktarılıyor...")
        
        try:
            # JSON dosyalarını içe aktar
            self.import_bargello_data()
            self.import_muscent_data()
            self.import_zara_data()
            
            # Benzerlik skorlarını hesapla
            self.calculate_all_similarities()
            
            logger.info("Tüm veriler başarıyla içe aktarıldı!")
            
        except Exception as e:
            logger.error(f"Veri içe aktarma hatası: {e}")
            db.session.rollback()
            raise

def run_import():
    """Veri içe aktarma işlemini çalıştır"""
    importer = DataImporter()
    importer.import_all_data() 