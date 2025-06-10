import requests
from bs4 import BeautifulSoup
import json
import logging
import urllib.parse
from difflib import SequenceMatcher

# Debugging için logging ayarı
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_bargello_data():
    with open('bargello_parfumler.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def translate_note(note):
    # Parfüm notaları için Türkçe-İngilizce eşleştirme sözlüğü
    note_translations = {
        # Meyveler
        'apple': 'elma',
        'pear': 'armut',
        'peach': 'şeftali',
        'mandarin': 'mandalina',
        'orange': 'portakal',
        'orange blossom': 'portakal çiçeği',
        'bergamot': 'bergamot',
        'lemon': 'limon',
        'grapefruit': 'greyfurt',
        'blackcurrant': 'siyah frenk üzümü',
        'raspberry': 'ahududu',
        'strawberry': 'çilek',
        'pineapple': 'ananas',
        'coconut': 'hindistan cevizi',
        'fig': 'incir',
        'plum': 'erik',
        'lychee': 'liçi',
        'mango': 'mango',

        # Çiçekler
        'rose': 'gül',
        'jasmine': 'yasemin',
        'lavender': 'lavanta',
        'violet': 'menekşe',
        'lily': 'zambak',
        'lily of the valley': 'vadi zambağı',
        'iris': 'süsen',
        'freesia': 'frezya',
        'magnolia': 'manolya',
        'gardenia': 'gardenya',
        'orchid': 'orkide',
        'peony': 'şakayık',
        'neroli': 'neroli',
        'geranium': 'sardunya',
        'lotus': 'lotus',

        # Baharatlar ve Otlar
        'vanilla': 'vanilya',
        'cinnamon': 'tarçın',
        'pepper': 'biber',
        'pink pepper': 'pembe biber',
        'cardamom': 'kakule',
        'saffron': 'safran',
        'nutmeg': 'muskat',
        'mint': 'nane',
        'rosemary': 'biberiye',
        'basil': 'fesleğen',
        'thyme': 'kekik',
        'sage': 'adaçayı',

        # Odunsu ve Reçineli
        'sandalwood': 'sandal ağacı',
        'cedar': 'sedir',
        'oud': 'ud',
        'patchouli': 'paçuli',
        'vetiver': 'vetiver',
        'amber': 'amber',
        'musk': 'misk',
        'leather': 'deri',
        'tobacco': 'tütün',
        'incense': 'tütsü',
        'woody notes': 'odunsu notalar',
        
        # Diğer
        'caramel': 'karamel',
        'chocolate': 'çikolata',
        'coffee': 'kahve',
        'almond': 'badem',
        'honey': 'bal',
        'sea notes': 'deniz notaları',
        'green notes': 'yeşil notalar',
        'powdery notes': 'pudramsı notalar',
        'spicy notes': 'baharatlı notalar',
        'floral notes': 'çiçeksi notalar',
        'fruity notes': 'meyvemsi notalar',
    }
    
    note = note.lower()
    # Tam eşleşme kontrolü
    if note in note_translations:
        return note_translations[note]
    
    # Kısmi eşleşme kontrolü
    for eng, tr in note_translations.items():
        if eng in note or note in eng:
            return tr
    
    return note

def calculate_note_similarity(parfumo_notes, bargello_notes):
    if not parfumo_notes or not any(bargello_notes.values()):
        return 0
    
    # Parfumo notalarını Türkçeye çevir
    parfumo_notes = [translate_note(note.lower()) for note in parfumo_notes]
    
    # Bargello notalarını düzenle
    all_bargello_notes = []
    for category in bargello_notes.values():
        if isinstance(category, str):
            notes = [n.strip().lower() for n in category.split(',')]
            all_bargello_notes.extend(notes)
        elif category != "Yok":
            all_bargello_notes.extend([n.strip().lower() for n in category])
    
    if not all_bargello_notes:
        return 0
    
    # Benzerlik hesapla
    matches = 0
    for p_note in parfumo_notes:
        for b_note in all_bargello_notes:
            if SequenceMatcher(None, p_note, b_note).ratio() > 0.8:
                matches += 1
                break
    
    return matches / max(len(parfumo_notes), len(all_bargello_notes))

def find_similar_bargello_perfumes(parfumo_notes, top_n=5):
    bargello_perfumes = load_bargello_data()
    similarities = []
    
    for perfume in bargello_perfumes:
        similarity = calculate_note_similarity(parfumo_notes, perfume['notalar'])
        if similarity > 0:
            similarities.append((perfume, similarity))
    
    # Sort by similarity score in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N matches
    return similarities[:top_n]

def scrape_parfumo_by_name_and_brand(brand, perfume_name):
    # URL'yi oluştur
    brand_url = urllib.parse.quote(brand.strip().replace(" ", "_"))
    perfume_url = urllib.parse.quote(perfume_name.strip().replace(" ", "_"))
    url = f"https://www.parfumo.com/Perfumes/{brand_url}/{perfume_url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Sayfayı çek
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Parfüm notalarını çek
        notes = [note.text.strip() for note in soup.select(".notes_list .clickable_note_img")]

        # Parfümörü çek
        perfumer_tag = soup.select_one(".w-100.mt-0-5.mb-3 a")
        perfumer = perfumer_tag.text.strip() if perfumer_tag else "Bilinmiyor"

        # Değerlendirme puanlarını çek
        ratings = {}
        rating_tags = soup.select(".barfiller_element")

        for tag in rating_tags:
            category = tag.select_one(".upper").text.strip()  # Kategori (Scent, Longevity, vb.)
            score = tag.select_one(".bold").text.strip()      # Puan (7.5, 7.8, vb.)
            ratings[category] = score

        # Cinsiyeti belirle
        gender = "Unisex"  # Varsayılan değer
        if soup.select_one(".p_gender_big i.fa-venus"):
            gender = "Kadın"
        elif soup.select_one(".p_gender_big i.fa-mars"):
            gender = "Erkek"

        # Add Bargello recommendations to the response
        similar_perfumes = find_similar_bargello_perfumes(notes)
        bargello_recommendations = []
        for perfume, similarity in similar_perfumes:
            recommendation = {
                "isim": perfume["isim"],
                "benzerlik": f"{similarity:.2%}",
                "notalar": perfume["notalar"]
            }
            bargello_recommendations.append(recommendation)
        
        # Sonuçları JSON olarak döndür
        perfume_data = {
            "url": url,
            "perfumer": perfumer,
            "notes": notes,
            "ratings": ratings,
            "gender": gender,
            "bargello_recommendations": bargello_recommendations
        }

        logging.info("Veri başarıyla çekildi.")
        return json.dumps(perfume_data, indent=4, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        logging.error(f"Bağlantı hatası: {e}")
    except Exception as e:
        logging.error(f"Bir hata oluştu: {e}")

# Script'in doğrudan çalıştırılması durumunda
if __name__ == "__main__":
    # Kullanıcıdan marka ve parfüm ismini al
    brand = input("Marka adı girin (örneğin: Giorgio Armani): ")
    perfume_name = input("Parfüm ismi girin (örneğin: Sì Passione Red Musk): ")

    # Parfüm verisini çek ve yazdır
    result = scrape_parfumo_by_name_and_brand(brand, perfume_name)
    if result:
        print(result)
    else:
        print(json.dumps({"error": "Parfüm bilgileri bulunamadı"}, ensure_ascii=False))

