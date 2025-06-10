import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Temel URL
base_url = "https://www.e-bargello.com"
kategori_url = "https://www.e-bargello.com/parfum-parfum-85?page={}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

parfum_links = []

# 1️⃣ Tüm parfüm linklerini çek
sayfa = 1
while True:
    url = kategori_url.format(sayfa)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    urunler = soup.select("div.item.item2.category-item a")

    if not urunler:
        break  # Sayfa boşsa dur

    for urun in urunler:
        link = urun["href"]

        # 🚨 Geçersiz linkleri filtrele
        if link.startswith("javascript") or link == "#":
            continue

        if link.startswith("/"):
            link = base_url + link  # Göreceli URL'yi tam URL'ye çevir

        parfum_links.append(link)

    sayfa += 1  # Sonraki sayfaya geç

print(f"Toplam {len(parfum_links)} geçerli parfüm bulundu.")

# 2️⃣ Parfüm detaylarını çek
parfum_data = []

for parfum_url in tqdm(parfum_links, desc="Parfümler Scrape Ediliyor"):
    try:
        parfum_response = requests.get(parfum_url, headers=headers, timeout=10)
        parfum_soup = BeautifulSoup(parfum_response.text, "html.parser")

        # Parfüm İsmi
        parfum_adi = parfum_soup.select_one("h4").text.strip() if parfum_soup.select_one("h4") else "Bilinmiyor"
        
        # Ürün Kodu
        urun_kodu = parfum_soup.select_one(".item-property-list li:nth-child(2)").text.split(":")[-1].strip() if parfum_soup.select_one(".item-property-list li:nth-child(2)") else "Bilinmiyor"
        
        # Stok Durumu
        stok_durumu = "Stokta var" if parfum_soup.select_one(".detail-stock .label-success") else "Stokta yok"
        
        # Puan
        puan_elementi = parfum_soup.select(".rate .rating-symbol-foreground span")
        puan = len(puan_elementi) if puan_elementi else "Bilinmiyor"
        
        # Notalar
        notalar = parfum_soup.select(".tab-content .tab-pane.active p")
        
        ust_notlar, orta_notlar, alt_notlar = "Yok", "Yok", "Yok"
        for nota in notalar:
            text = nota.text.strip()
            if text.startswith("Üst Nota"):
                ust_notlar = text.split(":")[-1].strip()
            elif text.startswith("Kalp Nota"):
                orta_notlar = text.split(":")[-1].strip()
            elif text.startswith("Dip Nota"):
                alt_notlar = text.split(":")[-1].strip()
        
        parfum_data.append({
            "isim": parfum_adi,
            "link": parfum_url,
            "urun_kodu": urun_kodu,
            "stok_durumu": stok_durumu,
            "puan": puan,
            "notalar": {
                "üst_notlar": ust_notlar,
                "orta_notlar": orta_notlar,
                "alt_notlar": alt_notlar
            }
        })

    except Exception as e:
        print(f"Hata: {parfum_url} işlenirken hata oluştu -> {e}")

# 3️⃣ JSON'a kaydet
with open("bargello_parfumler.json", "w", encoding="utf-8") as f:
    json.dump(parfum_data, f, ensure_ascii=False, indent=4)

print("✅ Veriler başarıyla 'bargello_parfumler.json' dosyasına kaydedildi!")