@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   PerfuMatch Kurulum Script'i (Windows)
echo ============================================================
echo.
echo Bu script PerfuMatch uygulamasını otomatik olarak kuracak.
echo Kurulum yaklaşık 5-10 dakika sürecek.
echo.
pause

echo.
echo Python kurulum script'i başlatılıyor...
echo.

python setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo HATA: Kurulum başarısız oldu!
    echo Lütfen Python'un yüklü olduğundan emin olun.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Kurulum tamamlandı!
echo ============================================================
echo.
echo Uygulamayı başlatmak için 'run.bat' dosyasını çalıştırın.
echo.
pause 