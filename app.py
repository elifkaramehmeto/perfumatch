from flask import Flask, request, jsonify, send_from_directory
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

app = Flask(__name__, static_folder='.')
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
    # Fiyat formatını düzenle
    price = perfume.get('fiyat', '')
    if isinstance(price, str) and '₺' in price:
        # "350,00₺" formatından sayısal değer çıkar
        try:
            price_num = float(price.replace('₺', '').replace(',', '.').strip())
        except:
            price_num = price
    else:
        price_num = price
    
    # Notaları düzenle
    notalar = perfume.get('notalar', {})
    if isinstance(notalar, dict):
        ust_notlar = notalar.get('üst_notlar', '') or notalar.get('Üst Notalar', '')
        orta_notlar = notalar.get('orta_notlar', '') or notalar.get('Orta Notalar', '')
        alt_notlar = notalar.get('alt_notlar', '') or notalar.get('Alt Notalar', '')
    else:
        ust_notlar = orta_notlar = alt_notlar = ''
    
    processed = {
        'id': f"bargello_{len(all_perfumes)}",
        'name': perfume.get('isim', ''),
        'brand': {'name': 'Bargello'},
        'price': price_num,
        'currency': 'TRY',
        'notes': {
            'top': [{'name': note.strip()} for note in ust_notlar.split(',') if note.strip()],
            'middle': [{'name': note.strip()} for note in orta_notlar.split(',') if note.strip()],
            'base': [{'name': note.strip()} for note in alt_notlar.split(',') if note.strip()]
        },
        'gender': perfume.get('cinsiyet', 'Unisex'),
        'family': perfume.get('aile', ''),
        'source': 'bargello',
        'product_url': perfume.get('link', '')
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
        'source': 'muscent',
        'product_url': perfume.get('url', '')
    }
    all_perfumes.append(processed)

# Process Zara perfumes
for perfume in zara_perfumes:
    # Zara notalarını düzenle - bazen liste, bazen dict olabiliyor
    notes_data = perfume.get('notes', {})
    if isinstance(notes_data, list):
        # Eğer notes bir liste ise, boş dict kullan
        top_notes = []
        middle_notes = []
        base_notes = []
    elif isinstance(notes_data, dict):
        top_notes = notes_data.get('top', [])
        middle_notes = notes_data.get('middle', [])
        base_notes = notes_data.get('base', [])
    else:
        top_notes = middle_notes = base_notes = []
    
    processed = {
        'id': f"zara_{len(all_perfumes)}",
        'name': perfume.get('name', ''),
        'brand': {'name': 'Zara'},
        'price': perfume.get('price', ''),
        'currency': 'TRY',
        'notes': {
            'top': [{'name': note} for note in top_notes if note],
            'middle': [{'name': note} for note in middle_notes if note],
            'base': [{'name': note} for note in base_notes if note]
        },
        'gender': perfume.get('gender', 'Unisex'),
        'family': perfume.get('family', ''),
        'source': 'zara',
        'product_url': perfume.get('url', '')
    }
    all_perfumes.append(processed)

logging.info(f"Loaded {len(all_perfumes)} perfumes from all sources")

# Static file routes
@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/search-results.html')
def search_results():
    """Serve search results page"""
    return send_from_directory('.', 'search-results.html')

@app.route('/perfume-detail.html')
def perfume_detail():
    """Serve perfume detail page"""
    return send_from_directory('.', 'perfume-detail.html')

# CSS ve JS dosyaları için özel route'lar
@app.route('/src/<path:filename>')
def src_files(filename):
    """Serve src directory files"""
    return send_from_directory('src', filename)

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
    """Search perfumes by name, notes, family, or advanced filters"""
    data = request.get_json()
    search_term = data.get('searchTerm', '').lower()
    search_type = data.get('searchType', 'name')
    gender = data.get('gender', 'all')
    family = data.get('family', 'all')
    selected_notes = data.get('selectedNotes', [])
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
        
        # Family filter
        if family != 'all':
            perfume_family = perfume.get('family', '').lower()
            if family.lower() not in perfume_family:
                continue
        
        # Notes filter (if selected notes are provided)
        if selected_notes:
            perfume_notes = []
            for note_type in ['top', 'middle', 'base']:
                for note in perfume['notes'].get(note_type, []):
                    note_name = note.get('name', '') if isinstance(note, dict) else str(note)
                    perfume_notes.append(note_name.lower())
            
            # Check if any of the selected notes match
            notes_match = any(selected_note.lower() in perfume_notes for selected_note in selected_notes)
            if not notes_match:
                continue
        
        # Search by type (only if search term is provided)
        if search_term:
            if search_type == 'name':
                if search_term in perfume['name'].lower():
                    match = True
            elif search_type == 'notes':
                # Search in all notes
                search_terms = [term.strip() for term in search_term.split(',')]
                for term in search_terms:
                    for note_type in ['top', 'middle', 'base']:
                        for note in perfume['notes'].get(note_type, []):
                            note_name = note.get('name', '') if isinstance(note, dict) else str(note)
                            if term in note_name.lower():
                                match = True
                                break
                        if match:
                            break
                    if match:
                        break
            elif search_type == 'brand':
                brand_name = perfume['brand'].get('name', '') if isinstance(perfume['brand'], dict) else str(perfume['brand'])
                if search_term in brand_name.lower():
                    match = True
            elif search_type == 'family':
                if search_term in perfume.get('family', '').lower():
                    match = True
        else:
            # If no search term, include all perfumes that pass filters
            match = True
        
        if match:
            results.append(perfume)
            if len(results) >= limit:
                break
    
    return jsonify({
        'results': results,
        'total': len(results),
        'search_term': search_term,
        'search_type': search_type,
        'family': family,
        'selected_notes': selected_notes
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
                note_name = note.get('name', '') if isinstance(note, dict) else str(note)
                if note_name:
                    all_notes.add(note_name)
        elif not note_type:
            for note_category in perfume['notes'].values():
                for note in note_category:
                    note_name = note.get('name', '') if isinstance(note, dict) else str(note)
                    if note_name:
                        all_notes.add(note_name)
    
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
        brand_name = perfume['brand'].get('name', '') if isinstance(perfume['brand'], dict) else str(perfume['brand'])
        if brand_name:
            brands.add(brand_name)
    
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

@app.route('/api/luxury-perfumes', methods=['GET'])
def get_luxury_perfumes():
    """Get list of luxury perfumes for the main page"""
    # For demo purposes, we'll create some mock luxury perfumes
    # In a real app, you'd have a separate luxury perfumes database
    luxury_perfumes = [
        {
            'id': 1,
            'name': 'Sauvage',
            'brand': {'name': 'Dior'},
            'price': 2500,
            'currency': 'TRY',
            'gender': 'men',
            'notes': {
                'top': [{'name': 'Bergamot'}, {'name': 'Pink Pepper'}],
                'middle': [{'name': 'Lavender'}, {'name': 'Geranium'}],
                'base': [{'name': 'Ambroxan'}, {'name': 'Cedar'}]
            }
        },
        {
            'id': 2,
            'name': 'Black Opium',
            'brand': {'name': 'Yves Saint Laurent'},
            'price': 2800,
            'currency': 'TRY',
            'gender': 'women',
            'notes': {
                'top': [{'name': 'Pink Pepper'}, {'name': 'Orange Blossom'}],
                'middle': [{'name': 'Jasmine'}, {'name': 'Coffee'}],
                'base': [{'name': 'Vanilla'}, {'name': 'Patchouli'}]
            }
        },
        {
            'id': 3,
            'name': 'Aventus',
            'brand': {'name': 'Creed'},
            'price': 4500,
            'currency': 'TRY',
            'gender': 'men',
            'notes': {
                'top': [{'name': 'Pineapple'}, {'name': 'Bergamot'}, {'name': 'Apple'}],
                'middle': [{'name': 'Rose'}, {'name': 'Dry Birch'}, {'name': 'Moroccan Jasmine'}],
                'base': [{'name': 'Oak Moss'}, {'name': 'Musk'}, {'name': 'Ambergris'}]
            }
        },
        {
            'id': 4,
            'name': 'La Vie Est Belle',
            'brand': {'name': 'Lancôme'},
            'price': 2200,
            'currency': 'TRY',
            'gender': 'women',
            'notes': {
                'top': [{'name': 'Pear'}, {'name': 'Black Currant'}],
                'middle': [{'name': 'Iris'}, {'name': 'Jasmine'}, {'name': 'Orange Blossom'}],
                'base': [{'name': 'Vanilla'}, {'name': 'Praline'}, {'name': 'Tonka Bean'}]
            }
        },
        {
            'id': 5,
            'name': 'Tom Ford Black Orchid',
            'brand': {'name': 'Tom Ford'},
            'price': 3200,
            'currency': 'TRY',
            'gender': 'unisex',
            'notes': {
                'top': [{'name': 'Truffle'}, {'name': 'Gardenia'}, {'name': 'Black Currant'}],
                'middle': [{'name': 'Orchid'}, {'name': 'Spices'}, {'name': 'Lotus Wood'}],
                'base': [{'name': 'Vanilla'}, {'name': 'Sandalwood'}, {'name': 'Patchouli'}]
            }
        },
        {
            'id': 6,
            'name': 'Bleu de Chanel',
            'brand': {'name': 'Chanel'},
            'price': 2600,
            'currency': 'TRY',
            'gender': 'men',
            'notes': {
                'top': [{'name': 'Grapefruit'}, {'name': 'Lemon'}, {'name': 'Mint'}],
                'middle': [{'name': 'Ginger'}, {'name': 'Nutmeg'}, {'name': 'Jasmine'}],
                'base': [{'name': 'Incense'}, {'name': 'Cedar'}, {'name': 'Sandalwood'}]
            }
        }
    ]
    
    return jsonify({'perfumes': luxury_perfumes})

@app.route('/api/luxury-perfume/<int:perfume_id>', methods=['GET'])
def get_luxury_perfume_detail(perfume_id):
    """Get detailed information about a luxury perfume"""
    luxury_perfumes = get_luxury_perfumes().get_json()['perfumes']
    
    for perfume in luxury_perfumes:
        if perfume['id'] == perfume_id:
            return jsonify({'perfume': perfume})
    
    return jsonify({'error': 'Luxury perfume not found'}), 404

@app.route('/api/alternative-perfume/<perfume_id>', methods=['GET'])
def get_alternative_perfume_detail(perfume_id):
    """Get detailed information about an alternative perfume"""
    for perfume in all_perfumes:
        if perfume['id'] == perfume_id:
            # Add product URL if available
            if perfume.get('source') == 'bargello':
                # Find original data for product URL
                for orig_perfume in bargello_perfumes:
                    if orig_perfume.get('isim') == perfume['name']:
                        perfume['product_url'] = orig_perfume.get('link', '')
                        break
            elif perfume.get('source') == 'zara':
                # Find original data for product URL
                for orig_perfume in zara_perfumes:
                    if orig_perfume.get('name') == perfume['name']:
                        perfume['product_url'] = orig_perfume.get('url', '')
                        break
            elif perfume.get('source') == 'muscent':
                # Find original data for product URL
                for orig_perfume in muscent_perfumes:
                    if orig_perfume.get('name') == perfume['name']:
                        perfume['product_url'] = orig_perfume.get('url', '')
                        break
            
            return jsonify({'perfume': perfume})
    
    return jsonify({'error': 'Alternative perfume not found'}), 404

@app.route('/api/find-alternatives', methods=['POST'])
def find_alternatives():
    """Find alternative perfumes for a luxury perfume"""
    data = request.get_json()
    luxury_perfume_id = data.get('luxury_perfume_id')
    min_similarity = data.get('min_similarity', 0.3)
    max_results = data.get('max_results', 10)
    
    # Get luxury perfume details
    luxury_perfume = None
    luxury_perfumes = get_luxury_perfumes().get_json()['perfumes']
    
    for perfume in luxury_perfumes:
        if perfume['id'] == luxury_perfume_id:
            luxury_perfume = perfume
            break
    
    if not luxury_perfume:
        return jsonify({'error': 'Luxury perfume not found'}), 404
    
    # Find alternatives based on notes similarity
    alternatives = []
    luxury_notes = []
    
    # Collect all luxury perfume notes
    for note_type in ['top', 'middle', 'base']:
        for note in luxury_perfume['notes'].get(note_type, []):
            luxury_notes.append(note['name'].lower())
    
    for perfume in all_perfumes:
        # Skip if same gender preference doesn't match
        if luxury_perfume['gender'] != 'unisex' and perfume.get('gender', '').lower() != luxury_perfume['gender']:
            continue
        
        # Calculate similarity based on notes
        perfume_notes = []
        for note_type in ['top', 'middle', 'base']:
            for note in perfume['notes'].get(note_type, []):
                perfume_notes.append(note['name'].lower())
        
        if not perfume_notes:
            continue
        
        # Calculate Jaccard similarity
        intersection = len(set(luxury_notes) & set(perfume_notes))
        union = len(set(luxury_notes) | set(perfume_notes))
        similarity = intersection / union if union > 0 else 0
        
        if similarity >= min_similarity:
            perfume_copy = perfume.copy()
            perfume_copy['similarity_score'] = similarity * 100
            
            # Add product URL if available
            if perfume.get('source') == 'bargello':
                for orig_perfume in bargello_perfumes:
                    if orig_perfume.get('isim') == perfume['name']:
                        perfume_copy['product_url'] = orig_perfume.get('link', '')
                        break
            elif perfume.get('source') == 'zara':
                for orig_perfume in zara_perfumes:
                    if orig_perfume.get('name') == perfume['name']:
                        perfume_copy['product_url'] = orig_perfume.get('url', '')
                        break
            elif perfume.get('source') == 'muscent':
                for orig_perfume in muscent_perfumes:
                    if orig_perfume.get('name') == perfume['name']:
                        perfume_copy['product_url'] = orig_perfume.get('url', '')
                        break
            
            alternatives.append(perfume_copy)
    
    # Sort by similarity and limit results
    alternatives.sort(key=lambda x: x['similarity_score'], reverse=True)
    alternatives = alternatives[:max_results]
    
    return jsonify({
        'luxury_perfume': luxury_perfume,
        'alternatives': alternatives,
        'total_found': len(alternatives)
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4421) 