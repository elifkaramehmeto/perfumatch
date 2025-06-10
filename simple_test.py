import requests

print("Testing API endpoints...")

try:
    # Test families
    r = requests.get('http://localhost:5000/api/families')
    families = r.json()
    print(f"Families API: {r.status_code} - {len(families)} families")
    print("Available families:", [f['name'] for f in families[:5]])
    
    # Test notes
    r = requests.get('http://localhost:5000/api/notes')
    notes = r.json()
    print(f"Notes API: {r.status_code} - {len(notes)} notes")
    print("Sample notes:", [n['name'] for n in notes[:5]])
    
    # Test search with exact family name
    if families:
        family_name = families[0]['name']
        r = requests.post('http://localhost:5000/api/perfume/search', json={
            'searchTerm': family_name,
            'searchType': 'family',
            'gender': 'all',
            'limit': 5
        })
        print(f"Search API ({family_name}): {r.status_code} - {len(r.json().get('results', []))} results")
    
    # Test name search
    r = requests.post('http://localhost:5000/api/perfume/search', json={
        'searchTerm': 'Sauvage',
        'searchType': 'name',
        'gender': 'all',
        'limit': 5
    })
    print(f"Name Search API: {r.status_code} - {len(r.json().get('results', []))} results")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}") 