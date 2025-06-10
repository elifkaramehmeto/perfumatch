#!/usr/bin/env python3
"""
Debug script to find the issue
"""

import requests
import json

def debug_families():
    """Debug families API"""
    print("🔍 Debugging families API...")
    
    try:
        response = requests.get('http://localhost:5000/api/families')
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            print(f"Type of data: {type(data)}")
            
            if 'families' in data:
                print(f"Families: {data['families']}")
                print(f"Type of families: {type(data['families'])}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_families() 