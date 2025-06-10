#!/usr/bin/env python3
"""
Test script for the new search functionality
"""

import requests
import json

def test_family_search():
    """Test family-based search"""
    print("🧪 Testing family search...")
    
    # Test floral family
    response = requests.post('http://localhost:5000/api/perfume/search', 
                           json={
                               'searchTerm': '',
                               'searchType': 'name',
                               'gender': 'all',
                               'family': 'floral',
                               'selectedNotes': [],
                               'limit': 5
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Floral family search: {data['total']} results")
        for perfume in data['results'][:3]:
            print(f"   - {perfume['name']} ({perfume.get('family', 'No family')})")
    else:
        print(f"❌ Family search failed: {response.status_code}")

def test_notes_search():
    """Test notes-based search"""
    print("\n🧪 Testing notes search...")
    
    # Test with common notes
    response = requests.post('http://localhost:5000/api/perfume/search', 
                           json={
                               'searchTerm': '',
                               'searchType': 'name',
                               'gender': 'all',
                               'family': 'all',
                               'selectedNotes': ['Gül', 'Vanilya'],
                               'limit': 5
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notes search (Gül, Vanilya): {data['total']} results")
        for perfume in data['results'][:3]:
            print(f"   - {perfume['name']}")
    else:
        print(f"❌ Notes search failed: {response.status_code}")

def test_combined_search():
    """Test combined search"""
    print("\n🧪 Testing combined search...")
    
    # Test with family + notes
    response = requests.post('http://localhost:5000/api/perfume/search', 
                           json={
                               'searchTerm': '',
                               'searchType': 'name',
                               'gender': 'women',
                               'family': 'floral',
                               'selectedNotes': ['Gül'],
                               'limit': 5
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Combined search (Women + Floral + Gül): {data['total']} results")
        for perfume in data['results'][:3]:
            print(f"   - {perfume['name']} ({perfume.get('gender', 'No gender')})")
    else:
        print(f"❌ Combined search failed: {response.status_code}")

def test_get_notes():
    """Test getting all notes"""
    print("\n🧪 Testing get notes...")
    
    response = requests.get('http://localhost:5000/api/notes')
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'notes' in data:
            print(f"✅ Notes API: {data['total']} notes available")
            print(f"   Sample notes: {data['notes'][:10]}")
        elif isinstance(data, list):
            print(f"✅ Notes API: {len(data)} notes available")
            print(f"   Sample notes: {[n.get('name', n) for n in data[:10]]}")
        else:
            print(f"✅ Notes API: {data}")
    else:
        print(f"❌ Notes API failed: {response.status_code}")

def test_get_families():
    """Test getting all families"""
    print("\n🧪 Testing get families...")
    
    response = requests.get('http://localhost:5000/api/families')
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'families' in data:
            print(f"✅ Families API: {data['total']} families available")
            print(f"   Families: {data['families']}")
        elif isinstance(data, list):
            print(f"✅ Families API: {len(data)} families available")
            print(f"   Families: {[f.get('name', f) for f in data[:5]]}")
        else:
            print(f"✅ Families API: {data}")
    else:
        print(f"❌ Families API failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing new search functionality...\n")
    
    try:
        test_get_families()
        test_get_notes()
        test_family_search()
        test_notes_search()
        test_combined_search()
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 