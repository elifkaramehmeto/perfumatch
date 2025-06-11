#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PerfuMatch Server Starter
Starts the PerfuMatch application on port 4421
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the PerfuMatch server"""
    print("🎯 PerfuMatch Sunucusu Başlatılıyor...")
    print("📍 Port: 4421")
    print("🌐 URL: http://localhost:4421")
    print("=" * 50)
    
    # Check if we have the required files
    if Path("server.py").exists():
        print("✅ server.py bulundu - Veritabanı destekli sürüm başlatılıyor...")
        try:
            subprocess.run([sys.executable, "server.py"], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Sunucu durduruldu.")
        except Exception as e:
            print(f"❌ Sunucu başlatma hatası: {e}")
            print("📝 app.py ile basit sürümü deneyin...")
            
    elif Path("app.py").exists():
        print("✅ app.py bulundu - Basit sürüm başlatılıyor...")
        try:
            subprocess.run([sys.executable, "app.py"], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Sunucu durduruldu.")
        except Exception as e:
            print(f"❌ Sunucu başlatma hatası: {e}")
    else:
        print("❌ Ne server.py ne de app.py bulunamadı!")
        print("📁 Lütfen doğru dizinde olduğunuzdan emin olun.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 