#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_alternatives():
    """Alternatifler API'sini test et"""
    
    print("🔍 Alternatifler API'si test ediliyor...")
    
    # Test 1: Gerçek parfüm ID'leri (3900'den başlıyor)
    test_ids = [3900, 3901, 3902, 3903, 3904, 3905, 3906, 3907, 3908, 3909]
    
    for perfume_id in test_ids:
        try:
            response = requests.get(f'http://localhost:5000/api/perfume/{perfume_id}/alternatives')
            print(f"📊 ID {perfume_id}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                alt_count = len(data.get('alternatives', []))
                print(f"✅ ID {perfume_id}: {alt_count} alternatif")
                
                if alt_count > 0:
                    print("📋 İlk alternatif:")
                    first_alt = data['alternatives'][0]
                    print(f"   - Lüks: {first_alt.get('luxury_perfume', {}).get('name', 'N/A')}")
                    print(f"   - Alternatif: {first_alt.get('alternative_perfume', {}).get('name', 'N/A')}")
                    print(f"   - Benzerlik: {first_alt.get('similarity_score', 'N/A')}%")
                    break
            else:
                print(f"❌ ID {perfume_id}: {response.text}")
                
        except Exception as e:
            print(f"❌ ID {perfume_id} hatası: {e}")
    
    # Test 2: Parfüm detaylarını kontrol et
    print("\n🔍 Parfüm detayları kontrol ediliyor...")
    for perfume_id in [3900, 3901, 3902]:
        try:
            response = requests.get(f'http://localhost:5000/api/perfume/{perfume_id}')
            if response.status_code == 200:
                data = response.json()
                print(f"📋 ID {perfume_id}: {data.get('name', 'N/A')} - {data.get('brand', {}).get('name', 'N/A')}")
            else:
                print(f"❌ ID {perfume_id}: Parfüm bulunamadı")
        except Exception as e:
            print(f"❌ ID {perfume_id} hatası: {e}")

if __name__ == "__main__":
    test_alternatives() 