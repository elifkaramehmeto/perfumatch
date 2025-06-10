#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PerfuMatch Kurulum Script'i
Bu script, PerfuMatch uygulamasını ilk kez kuran kullanıcılar için gerekli tüm adımları otomatik olarak gerçekleştirir.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json

class Colors:
    """Terminal renk kodları"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Renkli mesaj yazdır"""
    print(f"{color}{message}{Colors.END}")

def print_header(title):
    """Başlık yazdır"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored(f"  {title}", Colors.BOLD + Colors.CYAN)
    print_colored("="*60, Colors.CYAN)

def print_step(step_num, description):
    """Adım numarası ile açıklama yazdır"""
    print_colored(f"\n[{step_num}] {description}", Colors.YELLOW)

def print_success(message):
    """Başarı mesajı yazdır"""
    print_colored(f"✓ {message}", Colors.GREEN)

def print_error(message):
    """Hata mesajı yazdır"""
    print_colored(f"✗ {message}", Colors.RED)

def print_info(message):
    """Bilgi mesajı yazdır"""
    print_colored(f"ℹ {message}", Colors.BLUE)

def run_command(command, description="", check=True):
    """Komut çalıştır ve sonucu kontrol et"""
    try:
        if description:
            print_info(f"{description}...")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        
        if result.returncode == 0:
            if description:
                print_success(f"{description} tamamlandı")
            return True, result.stdout
        else:
            if description:
                print_error(f"{description} başarısız: {result.stderr}")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        if description:
            print_error(f"{description} başarısız: {e}")
        return False, str(e)

def check_python_version():
    """Python versiyonunu kontrol et"""
    print_step(1, "Python versiyonu kontrol ediliyor")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ gerekli. Mevcut versiyon: {version.major}.{version.minor}")
        print_info("Python'u güncelleyin: https://www.python.org/downloads/")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} uygun")
    return True

def check_node_version():
    """Node.js versiyonunu kontrol et"""
    print_step(2, "Node.js versiyonu kontrol ediliyor")
    
    success, output = run_command("node --version", check=False)
    if not success:
        print_error("Node.js bulunamadı")
        print_info("Node.js'i yükleyin: https://nodejs.org/")
        return False
    
    version = output.strip().replace('v', '')
    major_version = int(version.split('.')[0])
    
    if major_version < 16:
        print_error(f"Node.js 16+ gerekli. Mevcut versiyon: {version}")
        return False
    
    print_success(f"Node.js {version} uygun")
    return True

def check_postgresql():
    """PostgreSQL kurulumunu kontrol et"""
    print_step(3, "PostgreSQL kontrol ediliyor")
    
    # psql komutunu kontrol et
    success, output = run_command("psql --version", check=False)
    if not success:
        print_error("PostgreSQL bulunamadı")
        print_info("PostgreSQL'i yükleyin:")
        print_info("  Windows: https://www.postgresql.org/download/windows/")
        print_info("  macOS: brew install postgresql")
        print_info("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False
    
    print_success("PostgreSQL bulundu")
    return True

def create_virtual_environment():
    """Python sanal ortamı oluştur"""
    print_step(4, "Python sanal ortamı oluşturuluyor")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_info("Sanal ortam zaten mevcut")
        return True
    
    success, _ = run_command(f"{sys.executable} -m venv venv", "Sanal ortam oluşturuluyor")
    return success

def activate_virtual_environment():
    """Sanal ortamı aktifleştir"""
    print_step(5, "Sanal ortam aktifleştiriliyor")
    
    system = platform.system().lower()
    if system == "windows":
        activate_script = "venv\\Scripts\\activate.bat"
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    if not Path(activate_script).exists():
        print_error("Sanal ortam aktifleştirme script'i bulunamadı")
        return False, None, None
    
    print_success("Sanal ortam hazır")
    return True, pip_path, python_path

def install_python_dependencies(pip_path):
    """Python bağımlılıklarını yükle"""
    print_step(6, "Python bağımlılıkları yükleniyor")
    
    # requirements.txt'yi güncelle
    requirements = [
        "Flask==2.3.3",
        "Flask-CORS==4.0.0",
        "Flask-SQLAlchemy==3.0.5",
        "psycopg2-binary==2.9.7",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "python-dotenv==1.0.0",
        "lxml==4.9.3",
        "Werkzeug==2.3.7"
    ]
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))
    
    success, _ = run_command(f"{pip_path} install --upgrade pip", "pip güncelleniyor")
    if not success:
        return False
    
    success, _ = run_command(f"{pip_path} install -r requirements.txt", "Python paketleri yükleniyor")
    return success

def install_node_dependencies():
    """Node.js bağımlılıklarını yükle"""
    print_step(7, "Node.js bağımlılıkları yükleniyor")
    
    success, _ = run_command("npm install", "Node.js paketleri yükleniyor")
    return success

def create_env_file():
    """Environment dosyası oluştur"""
    print_step(8, "Environment dosyası oluşturuluyor")
    
    env_content = """# PerfuMatch Environment Variables

# Veritabanı Konfigürasyonu
DATABASE_URL=postgresql://perfumatch_user:perfumatch_pass@localhost:5432/perfumatch_db

# Flask Konfigürasyonu
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# API Konfigürasyonu
PARFUMO_API_DELAY=2
MAX_SEARCH_RESULTS=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/perfumatch.log
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print_success("Environment dosyası oluşturuldu (.env)")
    print_info("Gerekirse .env dosyasındaki ayarları düzenleyebilirsiniz")
    return True

def setup_database():
    """Veritabanını kur"""
    print_step(9, "Veritabanı kurulumu")
    
    print_info("PostgreSQL veritabanı ve kullanıcısı oluşturuluyor...")
    print_info("PostgreSQL şifrenizi girmeniz gerekebilir")
    
    # Veritabanı oluşturma komutları
    db_commands = [
        "CREATE DATABASE perfumatch_db;",
        "CREATE USER perfumatch_user WITH PASSWORD 'perfumatch_pass';",
        "GRANT ALL PRIVILEGES ON DATABASE perfumatch_db TO perfumatch_user;",
        "ALTER USER perfumatch_user CREATEDB;"
    ]
    
    for cmd in db_commands:
        success, _ = run_command(f'psql -U postgres -c "{cmd}"', check=False)
        if not success:
            print_info(f"Komut zaten çalıştırılmış olabilir: {cmd}")
    
    print_success("Veritabanı kurulumu tamamlandı")
    return True

def create_directories():
    """Gerekli dizinleri oluştur"""
    print_step(10, "Dizin yapısı oluşturuluyor")
    
    directories = [
        "logs",
        "uploads",
        "static/images",
        "static/css",
        "static/js",
        "data/backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Dizin oluşturuldu: {directory}")
    
    return True

def import_initial_data(python_path):
    """İlk veriyi içe aktar"""
    print_step(11, "İlk veriler içe aktarılıyor")
    
    if not Path("import_data.py").exists():
        print_error("import_data.py dosyası bulunamadı")
        return False
    
    print_info("Bu işlem birkaç dakika sürebilir...")
    success, _ = run_command(f"{python_path} import_data.py", "Veriler içe aktarılıyor")
    
    if success:
        print_success("İlk veriler başarıyla içe aktarıldı")
    else:
        print_error("Veri içe aktarma başarısız")
        print_info("Daha sonra manuel olarak 'python import_data.py' komutunu çalıştırabilirsiniz")
    
    return success

def create_run_scripts():
    """Çalıştırma script'leri oluştur"""
    print_step(12, "Çalıştırma script'leri oluşturuluyor")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch dosyası
        batch_content = """@echo off
echo PerfuMatch uygulamasi baslatiliyor...
call venv\\Scripts\\activate.bat
python server.py
pause
"""
        with open("run.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print_success("Windows çalıştırma dosyası oluşturuldu: run.bat")
        
    else:
        # Unix shell script
        shell_content = """#!/bin/bash
echo "PerfuMatch uygulaması başlatılıyor..."
source venv/bin/activate
python server.py
"""
        with open("run.sh", "w", encoding="utf-8") as f:
            f.write(shell_content)
        
        # Çalıştırma izni ver
        os.chmod("run.sh", 0o755)
        print_success("Unix çalıştırma dosyası oluşturuldu: run.sh")
    
    return True

def print_final_instructions():
    """Son talimatları yazdır"""
    print_header("KURULUM TAMAMLANDI!")
    
    print_colored("\n🎉 PerfuMatch başarıyla kuruldu!", Colors.GREEN + Colors.BOLD)
    
    print_colored("\n📋 Uygulamayı başlatmak için:", Colors.CYAN)
    
    system = platform.system().lower()
    if system == "windows":
        print_colored("   run.bat", Colors.WHITE + Colors.BOLD)
        print_colored("   veya: venv\\Scripts\\activate && python server.py", Colors.WHITE)
    else:
        print_colored("   ./run.sh", Colors.WHITE + Colors.BOLD)
        print_colored("   veya: source venv/bin/activate && python server.py", Colors.WHITE)
    
    print_colored("\n🌐 Uygulama adresleri:", Colors.CYAN)
    print_colored("   Ana sayfa: http://localhost:5000", Colors.WHITE + Colors.BOLD)
    print_colored("   API: http://localhost:5000/api/health", Colors.WHITE)
    
    print_colored("\n📁 Önemli dosyalar:", Colors.CYAN)
    print_colored("   .env - Environment ayarları", Colors.WHITE)
    print_colored("   logs/ - Uygulama logları", Colors.WHITE)
    print_colored("   requirements.txt - Python bağımlılıkları", Colors.WHITE)
    
    print_colored("\n🔧 Yararlı komutlar:", Colors.CYAN)
    print_colored("   Veri içe aktarma: python import_data.py", Colors.WHITE)
    print_colored("   Veritabanı kontrolü: python check_db.py", Colors.WHITE)
    print_colored("   Test çalıştırma: python -m pytest tests/", Colors.WHITE)
    
    print_colored("\n📖 Daha fazla bilgi için README.md dosyasını okuyun", Colors.YELLOW)
    print_colored("\n" + "="*60, Colors.CYAN)

def main():
    """Ana kurulum fonksiyonu"""
    print_header("PerfuMatch Kurulum Script'i")
    print_colored("Bu script, PerfuMatch uygulamasını ilk kez kuracak", Colors.WHITE)
    print_colored("Kurulum yaklaşık 5-10 dakika sürecek\n", Colors.WHITE)
    
    # Kullanıcı onayı
    response = input("Kuruluma devam etmek istiyor musunuz? (e/h): ").lower()
    if response not in ['e', 'evet', 'y', 'yes']:
        print_colored("Kurulum iptal edildi", Colors.YELLOW)
        return
    
    try:
        # Sistem gereksinimleri kontrolü
        if not check_python_version():
            return
        
        if not check_node_version():
            return
        
        if not check_postgresql():
            return
        
        # Kurulum adımları
        if not create_virtual_environment():
            return
        
        success, pip_path, python_path = activate_virtual_environment()
        if not success:
            return
        
        if not install_python_dependencies(pip_path):
            return
        
        if not install_node_dependencies():
            return
        
        if not create_env_file():
            return
        
        if not setup_database():
            return
        
        if not create_directories():
            return
        
        # Veri içe aktarma (opsiyonel)
        import_response = input("\nİlk verileri şimdi içe aktarmak istiyor musunuz? (e/h): ").lower()
        if import_response in ['e', 'evet', 'y', 'yes']:
            import_initial_data(python_path)
        else:
            print_info("Veri içe aktarma atlandı. Daha sonra 'python import_data.py' komutunu çalıştırabilirsiniz")
        
        if not create_run_scripts():
            return
        
        # Başarı mesajı
        print_final_instructions()
        
    except KeyboardInterrupt:
        print_colored("\n\nKurulum kullanıcı tarafından iptal edildi", Colors.YELLOW)
    except Exception as e:
        print_error(f"Beklenmeyen hata: {e}")
        print_info("Lütfen hata mesajını geliştiricilere bildirin")

if __name__ == "__main__":
    main() 