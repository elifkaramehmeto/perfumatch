import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import re
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('muscent_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def debug_request(url, response):
    """Request detaylarını logla"""
    logging.debug(f"URL: {url}")
    logging.debug(f"Status Code: {response.status_code}")
    logging.debug(f"Encoding: {response.encoding}")
    logging.debug(f"Headers: {dict(response.headers)}")

def debug_parse_results(soup, element_type):
    """Parsing sonuçlarını logla"""
    logging.debug(f"Parsing {element_type}")
    logging.debug(f"Found elements count: {len(soup) if soup else 0}")
    if soup and len(soup) > 0:
        logging.debug(f"First element sample: {soup[0]}")

def validate_data(data_dict):
    """Veri doğrulama ve loglama"""
    required_fields = ["isim", "link", "notalar"]
    missing_fields = [field for field in required_fields if not data_dict.get(field)]
    
    if missing_fields:
        logging.warning(f"Missing required fields: {missing_fields}")
        return False
    return True

# Temel URL
base_url = "https://muscent.com.tr"
kategori_url = "https://muscent.com.tr/magaza/page/{}/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

parfum_links = []

def create_session_with_retries():
    """Configure session with retry mechanism"""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def validate_page_content(soup, url):
    """Sayfa içeriğinin geçerliliğini kontrol et"""
    if not soup.select("div.thumbnail"):
        logging.warning(f"Page content validation failed for {url}")
        return False
    return True

# 1️⃣ Tüm parfüm linklerini çek
def get_all_perfume_links():
    session = create_session_with_retries()
    sayfa = 1
    consecutive_empty_pages = 0
    max_empty_pages = 3  # Ardışık boş sayfa limiti

    while True:
        try:
            url = kategori_url.format(sayfa)
            logging.info(f"Fetching page {sayfa}: {url}")
            
            response = session.get(url, headers=headers, timeout=(10, 30))
            debug_request(url, response)
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            if not validate_page_content(soup, url):
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    logging.info(f"Reached {max_empty_pages} consecutive empty pages. Stopping.")
                    break
                continue
            
            consecutive_empty_pages = 0  # Reset counter on valid page
            
            urunler = soup.select("div.thumbnail a.woocommerce-LoopProduct-link")
            debug_parse_results(urunler, f"product links on page {sayfa}")
            
            if not urunler:
                logging.info(f"No products found on page {sayfa}. Stopping.")
                break
            
            new_links = 0
            for urun in urunler:
                link = urun["href"]
                if link not in parfum_links:
                    parfum_links.append(link)
                    new_links += 1
            
            logging.info(f"Found {new_links} new products on page {sayfa}")
            
            if new_links == 0:
                logging.info("No new products found. Might have reached the end.")
                consecutive_empty_pages += 1
            
            sayfa += 1
            time.sleep(2)  # Increased sleep time
            
        except requests.Timeout:
            logging.error(f"Timeout while fetching page {sayfa}", exc_info=True)
            time.sleep(5)  # Longer wait on timeout
            continue
        except requests.RequestException as e:
            logging.error(f"Request error on page {sayfa}: {str(e)}", exc_info=True)
            if "Too Many Requests" in str(e):
                time.sleep(60)  # Rate limit handling
            continue
        except Exception as e:
            logging.error(f"Unexpected error on page {sayfa}: {str(e)}", exc_info=True)
            break

    logging.info(f"Completed link collection. Total links found: {len(parfum_links)}")

# 2️⃣ Parfüm detaylarını çek
def get_perfume_details():
    parfum_data = []
    
    for parfum_url in tqdm(parfum_links, desc="Parfümler Scrape Ediliyor"):
        try:
            logging.info(f"Fetching: {parfum_url}")
            response = requests.get(parfum_url, headers=headers, timeout=10)
            debug_request(parfum_url, response)
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Parfüm adı
            parfum_adi = soup.select_one("h1.product_title")
            logging.debug(f"Found product title: {parfum_adi.text.strip() if parfum_adi else 'Not found'}")
            
            # Fiyat aralığı
            fiyat_element = soup.select_one("div.price")
            fiyat = fiyat_element.text.strip() if fiyat_element else "Belirtilmemiş"
            
            # Puan
            puan_element = soup.select_one("div.review-rating-average")
            puan = puan_element.text.strip() if puan_element else "Belirtilmemiş"
            
            # Stok durumu (varsayılan olarak True, çünkü sitede genelde stok bilgisi yok)
            stok_durumu = True
            
            # Açıklama ve notalar
            aciklama_element = soup.select_one("#tab-description .accordion-content p")
            aciklama = aciklama_element.text.strip() if aciklama_element else ""
            
            # Notaları düzenli ifadeler ile çıkar
            notalar = {
                "en_yogun_notalar": "",
                "cinsiyet": "",
                "akorlar": ""
            }
            
            if aciklama:
                en_yogun_match = re.search(r'En Yoğun Hissedilen Notalar:(.*?)(?:\n|$)', aciklama)
                cinsiyet_match = re.search(r'Cinsiyet:(.*?)(?:\n|$)', aciklama)
                akorlar_match = re.search(r'Akorlar:(.*?)(?:\n|$)', aciklama)
                
                notalar["en_yogun_notalar"] = en_yogun_match.group(1).strip() if en_yogun_match else ""
                notalar["cinsiyet"] = cinsiyet_match.group(1).strip() if cinsiyet_match else ""
                notalar["akorlar"] = akorlar_match.group(1).strip() if akorlar_match else ""
            
            # Etiketler
            etiketler = [tag.text.strip() for tag in soup.select(".tagged_as.meta-item a")]
            
            data = {
                "isim": parfum_adi.text.strip() if parfum_adi else "Bilinmiyor",
                "link": parfum_url,
                "fiyat": fiyat,
                "puan": puan,
                "stok_durumu": stok_durumu,
                "notalar": notalar,
                "etiketler": etiketler,
                "aciklama": aciklama
            }

            if validate_data(data):
                parfum_data.append(data)
                logging.info(f"Successfully processed: {data['isim']}")
            else:
                logging.warning(f"Skipping invalid data for URL: {parfum_url}")

            time.sleep(1)  # Siteyi yormamak için bekleme

        except requests.Timeout:
            logging.error(f"Timeout error for {parfum_url}")
        except requests.RequestException as e:
            logging.error(f"Request error for {parfum_url}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error for {parfum_url}: {str(e)}", exc_info=True)
    
    return parfum_data

# 3️⃣ Ana fonksiyon
def main():
    logging.info("Starting Muscent parfume scraping")
    try:
        # Parfüm linklerini topla
        get_all_perfume_links()
        
        # Parfüm detaylarını çek
        parfum_data = get_perfume_details()
        
        # JSON'a kaydet
        with open("muscent_parfumler.json", "w", encoding="utf-8") as f:
            json.dump(parfum_data, f, ensure_ascii=False, indent=4)
        
        logging.info("✅ Scraping completed successfully")
        print("✅ Veriler başarıyla 'muscent_parfumler.json' dosyasına kaydedildi!")
    except Exception as e:
        logging.error("❌ Scraping failed", exc_info=True)
        raise

if __name__ == "__main__":
    main()
