from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load data files
def load_bargello_data():
    """Load Bargello perfume data"""
    try:
        with open('bargello_parfumler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("bargello_parfumler.json not found")
        return []

def load_muscent_data():
    """Load Muscent perfume data"""
    try:
        with open('muscent_parfumler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("muscent_parfumler.json not found")
        return []

def load_zara_data():
    """Load Zara perfume data"""
    zara_files = [
        'zara_perfumes.json',
        'zara_perfumes_20250610_005616.json',
        'zara_mens_perfumes_20250610_020110.json'
    ]
    
    all_data = []
    for file in zara_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except FileNotFoundError:
            logging.warning(f"{file} not found")
    
    return all_data

# Load all data at startup
bargello_perfumes = load_bargello_data()
muscent_perfumes = load_muscent_data()
zara_perfumes = load_zara_data()

# Combine all perfumes
all_perfumes = []

# Process Bargello perfumes
for perfume in bargello_perfumes:
    processed = {
        'id': f"bargello_{len(all_perfumes)}",
        'name': perfume.get('isim', ''),
        'brand': {'name': 'Bargello'},
        'price': perfume.get('fiyat', ''),
        'currency': 'TRY',
        'notes': {
            'top': [{'name': note} for note in perfume.get('notalar', {}).get('Üst Notalar', '').split(',') if note.strip()],
            'middle': [{'name': note} for note in perfume.get('notalar', {}).get('Orta Notalar', '').split(',') if note.strip()],
            'base': [{'name': note} for note in perfume.get('notalar', {}).get('Alt Notalar', '').split(',') if note.strip()]
        },
        'gender': perfume.get('cinsiyet', 'Unisex'),
        'family': perfume.get('aile', ''),
        'source': 'bargello'
    }
    all_perfumes.append(processed)

# Process Muscent perfumes
for perfume in muscent_perfumes:
    processed = {
        'id': f"muscent_{len(all_perfumes)}",
        'name': perfume.get('name', ''),
        'brand': {'name': 'Muscent'},
        'price': perfume.get('price', ''),
        'currency': 'TRY',
        'notes': {
            'top': [{'name': note} for note in perfume.get('top_notes', [])],
            'middle': [{'name': note} for note in perfume.get('middle_notes', [])],
            'base': [{'name': note} for note in perfume.get('base_notes', [])]
        },
        'gender': perfume.get('gender', 'Unisex'),
        'family': perfume.get('family', ''),
        'source': 'muscent'
    }
    all_perfumes.append(processed)

# Process Zara perfumes
for perfume in zara_perfumes:
    processed = {
        'id': f"zara_{len(all_perfumes)}",
        'name': perfume.get('name', ''),
        'brand': {'name': 'Zara'},
        'price': perfume.get('price', ''),
        'currency': 'TRY',
        'notes': {
            'top': [{'name': note} for note in perfume.get('notes', {}).get('top', [])],
            'middle': [{'name': note} for note in perfume.get('notes', {}).get('middle', [])],
            'base': [{'name': note} for note in perfume.get('notes', {}).get('base', [])]
        },
        'gender': perfume.get('gender', 'Unisex'),
        'family': perfume.get('family', ''),
        'source': 'zara'
    }
    all_perfumes.append(processed)

logging.info(f"Loaded {len(all_perfumes)} perfumes from all sources")

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'PerfuMatch API is running',
        'perfumes_count': len(all_perfumes)
    })

@app.route('/api/perfume/search', methods=['POST'])
def search_perfumes():
    """Search perfumes by name, notes, or family"""
    data = request.get_json()
    search_term = data.get('searchTerm', '').lower()
    search_type = data.get('searchType', 'name')
    gender = data.get('gender', 'all')
    limit = data.get('limit', 10)
    
    results = []
    
    for perfume in all_perfumes:
        match = False
        
        # Gender filter
        if gender != 'all':
            perfume_gender = perfume.get('gender', '').lower()
            if gender == 'women' and perfume_gender not in ['kadın', 'women', 'female']:
                continue
            elif gender == 'men' and perfume_gender not in ['erkek', 'men', 'male']:
                continue
        
        # Search by type
        if search_type == 'name':
            if search_term in perfume['name'].lower():
                match = True
        elif search_type == 'notes':
            # Search in all notes
            search_terms = [term.strip() for term in search_term.split(',')]
            for term in search_terms:
                for note_type in ['top', 'middle', 'base']:
                    for note in perfume['notes'].get(note_type, []):
                        if term in note['name'].lower():
                            match = True
                            break
                    if match:
                        break
                if match:
                    break
        elif search_type == 'family':
            if search_term in perfume.get('family', '').lower():
                match = True
        
        if match:
            results.append(perfume)
            if len(results) >= limit:
                break
    
    return jsonify({
        'results': results,
        'total': len(results),
        'search_term': search_term,
        'search_type': search_type
    })

@app.route('/api/perfume/parfumo-search', methods=['POST'])
def parfumo_search():
    """Search perfume on Parfumo.com and get Bargello recommendations"""
    data = request.get_json()
    brand = data.get('brand', '')
    perfume_name = data.get('perfumeName', '')
    
    try:
        # Import the scraping function
        from scrapping.request_branded import scrape_parfumo_by_name_and_brand
        
        result = scrape_parfumo_by_name_and_brand(brand, perfume_name)
        if result:
            return jsonify(json.loads(result))
        else:
            return jsonify({'error': 'Parfüm bulunamadı'}), 404
    except Exception as e:
        logging.error(f"Parfumo search error: {e}")
        return jsonify({'error': 'Arama sırasında bir hata oluştu'}), 500

@app.route('/api/popular-perfumes', methods=['GET'])
def get_popular_perfumes():
    """Get popular perfumes"""
    # Return a sample of perfumes as popular ones
    popular = all_perfumes[:10] if len(all_perfumes) >= 10 else all_perfumes
    return jsonify({
        'perfumes': popular,
        'total': len(popular)
    })

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get perfume notes by type"""
    note_type = request.args.get('type')
    
    all_notes = set()
    
    for perfume in all_perfumes:
        if note_type and note_type in perfume['notes']:
            for note in perfume['notes'][note_type]:
                all_notes.add(note['name'])
        elif not note_type:
            for note_category in perfume['notes'].values():
                for note in note_category:
                    all_notes.add(note['name'])
    
    return jsonify({
        'notes': sorted(list(all_notes)),
        'type': note_type,
        'total': len(all_notes)
    })

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Get all brands"""
    brands = set()
    for perfume in all_perfumes:
        brands.add(perfume['brand']['name'])
    
    return jsonify({
        'brands': sorted(list(brands)),
        'total': len(brands)
    })

@app.route('/api/families', methods=['GET'])
def get_families():
    """Get all perfume families"""
    families = set()
    for perfume in all_perfumes:
        if perfume.get('family'):
            families.add(perfume['family'])
    
    return jsonify({
        'families': sorted(list(families)),
        'total': len(families)
    })

@app.route('/api/perfume/<perfume_id>', methods=['GET'])
def get_perfume_detail(perfume_id):
    """Get perfume details by ID"""
    for perfume in all_perfumes:
        if perfume['id'] == perfume_id:
            return jsonify(perfume)
    
    return jsonify({'error': 'Parfüm bulunamadı'}), 404

@app.route('/api/perfume/<perfume_id>/alternatives', methods=['GET'])
def get_perfume_alternatives(perfume_id):
    """Get alternatives for a perfume"""
    # Find the perfume
    target_perfume = None
    for perfume in all_perfumes:
        if perfume['id'] == perfume_id:
            target_perfume = perfume
            break
    
    if not target_perfume:
        return jsonify({'error': 'Parfüm bulunamadı'}), 404
    
    # Find similar perfumes based on notes
    alternatives = []
    target_notes = []
    
    for note_type in ['top', 'middle', 'base']:
        for note in target_perfume['notes'].get(note_type, []):
            target_notes.append(note['name'].lower())
    
    for perfume in all_perfumes:
        if perfume['id'] == perfume_id:
            continue
        
        perfume_notes = []
        for note_type in ['top', 'middle', 'base']:
            for note in perfume['notes'].get(note_type, []):
                perfume_notes.append(note['name'].lower())
        
        # Calculate similarity
        common_notes = set(target_notes) & set(perfume_notes)
        if len(common_notes) > 0:
            similarity = len(common_notes) / max(len(target_notes), len(perfume_notes))
            if similarity > 0.3:  # At least 30% similarity
                alternatives.append({
                    'perfume': perfume,
                    'similarity': similarity,
                    'common_notes': list(common_notes)
                })
    
    # Sort by similarity
    alternatives.sort(key=lambda x: x['similarity'], reverse=True)
    
    return jsonify({
        'alternatives': alternatives[:5],  # Top 5 alternatives
        'total': len(alternatives)
    })

@app.route('/api/perfume/<perfume_id>/rate', methods=['POST'])
def rate_perfume(perfume_id):
    """Rate a perfume"""
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # In a real application, you would save this to a database
    logging.info(f"Perfume {perfume_id} rated: {rating}, comment: {comment}")
    
    return jsonify({
        'message': 'Değerlendirme kaydedildi',
        'perfume_id': perfume_id,
        'rating': rating
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 