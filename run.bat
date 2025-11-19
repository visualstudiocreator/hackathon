@echo off
REM Скрипт запуска для Windows

echo ========================================
echo   Препродакшн Анализатор Сценариев
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.8 или выше с https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python найден

REM Проверка наличия зависимостей
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ПРЕДУПРЕЖДЕНИЕ] Зависимости не установлены
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости
        pause
        exit /b 1
    )
)

echo [OK] Зависимости установлены

REM Запуск приложения
echo.
echo ========================================
echo   Запуск сервера...
echo ========================================
echo.
echo Откройте в браузере: http://localhost:8000
echo.
echo Для остановки нажмите Ctrl+C
echo.
echo ========================================
echo.

python app.py

