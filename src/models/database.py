#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from datetime import datetime
import os

db = SQLAlchemy()

class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # luxury, alternative
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    perfumes = db.relationship('Perfume', backref='brand', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PerfumeFamily(db.Model):
    __tablename__ = 'perfume_families'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    perfumes = db.relationship('Perfume', backref='family', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # top, middle, base
    category = db.Column(db.String(50))  # floral, woody, citrus, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Perfume(db.Model):
    __tablename__ = 'perfumes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('perfume_families.id'))
    gender = db.Column(db.String(20), nullable=False)  # men, women, unisex
    price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='TRY')
    volume = db.Column(db.Integer)  # ml
    concentration = db.Column(db.String(20))  # EDP, EDT, Parfum
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    product_url = db.Column(db.Text)
    stock_status = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Numeric(3, 2))
    perfumer = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    longevity_rating = db.Column(db.Numeric(3, 2))
    sillage_rating = db.Column(db.Numeric(3, 2))
    bottle_rating = db.Column(db.Numeric(3, 2))
    value_rating = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    notes = db.relationship('PerfumeNote', backref='perfume', lazy=True, cascade='all, delete-orphan')
    luxury_similarities = db.relationship('PerfumeSimilarity', 
                                        foreign_keys='PerfumeSimilarity.luxury_perfume_id',
                                        backref='luxury_perfume', lazy=True)
    alternative_similarities = db.relationship('PerfumeSimilarity',
                                             foreign_keys='PerfumeSimilarity.alternative_perfume_id',
                                             backref='alternative_perfume', lazy=True)
    
    def to_dict(self, include_notes=True, include_similarities=False):
        result = {
            'id': self.id,
            'name': self.name,
            'brand': self.brand.to_dict() if self.brand else None,
            'family': self.family.to_dict() if self.family else None,
            'gender': self.gender,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'volume': self.volume,
            'concentration': self.concentration,
            'description': self.description,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'stock_status': self.stock_status,
            'rating': float(self.rating) if self.rating else None,
            'perfumer': self.perfumer,
            'release_year': self.release_year,
            'longevity_rating': float(self.longevity_rating) if self.longevity_rating else None,
            'sillage_rating': float(self.sillage_rating) if self.sillage_rating else None,
            'bottle_rating': float(self.bottle_rating) if self.bottle_rating else None,
            'value_rating': float(self.value_rating) if self.value_rating else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_notes:
            result['notes'] = {
                'top': [pn.note.to_dict() for pn in self.notes if pn.note.type == 'top'],
                'middle': [pn.note.to_dict() for pn in self.notes if pn.note.type == 'middle'],
                'base': [pn.note.to_dict() for pn in self.notes if pn.note.type == 'base']
            }
        
        if include_similarities:
            result['alternatives'] = [sim.to_dict() for sim in self.luxury_similarities]
        
        return result

class PerfumeNote(db.Model):
    __tablename__ = 'perfume_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    perfume_id = db.Column(db.Integer, db.ForeignKey('perfumes.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    intensity = db.Column(db.Integer, default=5)  # 1-10 arası
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    note = db.relationship('Note', backref='perfume_notes')
    
    __table_args__ = (db.UniqueConstraint('perfume_id', 'note_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'perfume_id': self.perfume_id,
            'note': self.note.to_dict() if self.note else None,
            'intensity': self.intensity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PerfumeSimilarity(db.Model):
    __tablename__ = 'perfume_similarities'
    
    id = db.Column(db.Integer, primary_key=True)
    luxury_perfume_id = db.Column(db.Integer, db.ForeignKey('perfumes.id'), nullable=False)
    alternative_perfume_id = db.Column(db.Integer, db.ForeignKey('perfumes.id'), nullable=False)
    similarity_score = db.Column(db.Numeric(5, 2))  # 0-100 arası
    note_similarity = db.Column(db.Numeric(5, 2))
    family_similarity = db.Column(db.Numeric(5, 2))
    gender_match = db.Column(db.Boolean)
    price_difference = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('luxury_perfume_id', 'alternative_perfume_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'luxury_perfume': self.luxury_perfume.to_dict(include_notes=True, include_similarities=False) if self.luxury_perfume else None,
            'alternative_perfume': self.alternative_perfume.to_dict(include_notes=True, include_similarities=False) if self.alternative_perfume else None,
            'similarity_score': float(self.similarity_score) if self.similarity_score else None,
            'note_similarity': float(self.note_similarity) if self.note_similarity else None,
            'family_similarity': float(self.family_similarity) if self.family_similarity else None,
            'gender_match': self.gender_match,
            'price_difference': float(self.price_difference) if self.price_difference else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserRating(db.Model):
    __tablename__ = 'user_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    perfume_id = db.Column(db.Integer, db.ForeignKey('perfumes.id'))
    similarity_id = db.Column(db.Integer, db.ForeignKey('perfume_similarities.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 arası
    comment = db.Column(db.Text)
    helpful_count = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45))  # IPv6 için
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    perfume = db.relationship('Perfume', backref='user_ratings')
    similarity = db.relationship('PerfumeSimilarity', backref='user_ratings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'perfume_id': self.perfume_id,
            'similarity_id': self.similarity_id,
            'rating': self.rating,
            'comment': self.comment,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(200))
    search_type = db.Column(db.String(20))  # name, notes, family
    results_count = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'search_term': self.search_term,
            'search_type': self.search_type,
            'results_count': self.results_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Yardımcı fonksiyonlar
def init_db(app):
    """Veritabanını başlat"""
    db.init_app(app)
    
    with app.app_context():
        # Tabloları oluştur (eğer yoksa)
        db.create_all()

def get_db_connection():
    """Veritabanı bağlantısını al"""
    return db

def search_perfumes_by_name(search_term, limit=10):
    """İsme göre parfüm ara"""
    return Perfume.query.join(Brand).filter(
        db.or_(
            Perfume.name.ilike(f'%{search_term}%'),
            Brand.name.ilike(f'%{search_term}%')
        )
    ).limit(limit).all()

def search_perfumes_by_notes(note_names, limit=10):
    """Notalara göre parfüm ara"""
    return Perfume.query.join(PerfumeNote).join(Note).filter(
        Note.name.in_(note_names)
    ).group_by(Perfume.id).having(
        func.count(Note.id) >= len(note_names) * 0.5  # En az %50 nota eşleşmesi
    ).limit(limit).all()

def search_perfumes_by_family(family_name, limit=10):
    """Aileye göre parfüm ara"""
    return Perfume.query.join(PerfumeFamily).filter(
        PerfumeFamily.name.ilike(f'%{family_name}%')
    ).limit(limit).all()

def get_similar_perfumes(perfume_id, limit=5):
    """Benzer parfümleri getir"""
    return PerfumeSimilarity.query.filter_by(
        luxury_perfume_id=perfume_id
    ).order_by(
        PerfumeSimilarity.similarity_score.desc()
    ).limit(limit).all()

def calculate_similarity_score(perfume1, perfume2):
    """İki parfüm arasındaki benzerlik skorunu hesapla"""
    score = 0
    
    # Cinsiyet eşleşmesi (30 puan)
    if perfume1.gender == perfume2.gender or perfume1.gender == 'unisex' or perfume2.gender == 'unisex':
        score += 30
    
    # Aile eşleşmesi (25 puan)
    if perfume1.family_id == perfume2.family_id:
        score += 25
    
    # Nota benzerliği (45 puan)
    notes1 = set([pn.note.name for pn in perfume1.notes])
    notes2 = set([pn.note.name for pn in perfume2.notes])
    
    if notes1 and notes2:
        common_notes = len(notes1.intersection(notes2))
        total_notes = len(notes1.union(notes2))
        note_similarity = (common_notes / total_notes) * 45
        score += note_similarity
    
    return min(score, 100)  # Maksimum 100 puan 