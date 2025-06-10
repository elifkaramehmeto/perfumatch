# Bargello Parfüm Veritabanı Dokümantasyonu

## Genel Bakış
Bu dokümantasyon, Bargello parfümleri hakkında detaylı bilgiler içeren bir JSON veritabanı için hazırlanmıştır. Veritabanı, parfümlerin isimleri, ürün kodları, stok durumları, puanları ve koku notaları gibi çeşitli bilgileri saklamaktadır.

## Veri Yapısı
Veritabanındaki her parfüm kaydı aşağıdaki alanları içerir:

### Ana Alanlar
- `isim`: Parfümün adı
- `link`: e-bargello.com'daki ürün URL'si
- `urun_kodu`: Ürün kodu
- `stok_durumu`: Stok durumu (genellikle "Stokta var" veya "Stokta yok")
- `puan`: Değerlendirme puanı (genellikle "Bilinmiyor")

### Koku Notaları (`notalar`)
Üç alt kategoriden oluşur:
- `üst_notlar`: Parfümün ilk açıldığında hissedilen uçucu notaları
- `orta_notlar`: Parfümün karakterini oluşturan kalp notaları
- `alt_notlar`: Parfümün kalıcılığını sağlayan temel notalar

## Parfüm Kategorileri
Veritabanı farklı parfüm türlerini içerir:
- Kadın parfümleri (KADIN): Çiçeksi ve tatlı notalar ağırlıklı
- Erkek parfümleri (ERKEK): Odunsu ve baharatlı notalar ağırlıklı
- Unisex parfümler (UNISEX): Her iki cinsiyete uygun dengeli notalar

## Koku Tipleri
Parfümler farklı koku ailelerine göre sınıflandırılır:
- FLORAL (Çiçeksi): Yasemin, gül, zambak gibi çiçek notaları
- ORIENTAL (Oryantal): Baharat, vanilya, amber notaları
- WOODY (Odunsu): Sandal ağacı, sedir, vetiver notaları
- FRESH (Ferah): Narenciye, deniz, yeşil notalar

## Veri Toplama Süreci
fetch_bargello.py dosyası aşağıdaki işlemleri gerçekleştirir:
1. e-bargello.com'dan ürün sayfaları taranır
    - Ürün listesi sayfaları dolaşılır
    - Her ürünün detay sayfası ziyaret edilir
2. Web kazıma yöntemiyle bilgiler çıkarılır
    - BeautifulSoup kütüphanesi kullanılır
    - HTML elementlerinden veri ayıklanır
3. Veriler yapılandırılmış JSON formatında saklanır
    - Parfüm bilgileri normalize edilir
    - JSON dosyasına kaydedilir

## Örnek Kayıt
```json
{
     "isim": "BARGELLO FLEUR DE PERLE KADIN 50 ml PARFÜM EDP",
     "link": "https://www.e-bargello.com/bargello-fleur-de-perle-kadin-50-ml-parfum-edp-1503",
     "urun_kodu": "3010001491",
     "stok_durumu": "Stokta var",
     "puan": "Bilinmiyor",
     "notalar": {
          "üst_notlar": "Bergamot, Mandalina, Pembe Biber",
          "orta_notlar": "Yasemin, İnci Çiçeği",
          "alt_notlar": "Misk, Sandal Ağacı"
     }
}
```
