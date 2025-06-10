#!/bin/bash

# PerfuMatch Kurulum Script'i (Unix/Linux/macOS)

echo ""
echo "============================================================"
echo "  PerfuMatch Kurulum Script'i (Unix/Linux/macOS)"
echo "============================================================"
echo ""
echo "Bu script PerfuMatch uygulamasını otomatik olarak kuracak."
echo "Kurulum yaklaşık 5-10 dakika sürecek."
echo ""

read -p "Kuruluma devam etmek istiyor musunuz? (e/h): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[EeYy]$ ]]; then
    echo "Kurulum iptal edildi."
    exit 1
fi

echo ""
echo "Python kurulum script'i başlatılıyor..."
echo ""

# Python script'ini çalıştır
python3 setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "HATA: Kurulum başarısız oldu!"
    echo "Lütfen Python 3.8+ yüklü olduğundan emin olun."
    echo ""
    exit 1
fi

echo ""
echo "============================================================"
echo "  Kurulum tamamlandı!"
echo "============================================================"
echo ""
echo "Uygulamayı başlatmak için './run.sh' komutunu çalıştırın."
echo "" 