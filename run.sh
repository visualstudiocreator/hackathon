#!/bin/bash
# Скрипт запуска для Linux/Mac

echo "========================================"
echo "  Препродакшн Анализатор Сценариев"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null
then
    echo "[ОШИБКА] Python3 не найден!"
    echo "Установите Python 3.8 или выше"
    exit 1
fi

echo "[OK] Python найден"

# Проверка наличия зависимостей
python3 -c "import fastapi" &> /dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "[ПРЕДУПРЕЖДЕНИЕ] Зависимости не установлены"
    echo "Установка зависимостей..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ОШИБКА] Не удалось установить зависимости"
        exit 1
    fi
fi

echo "[OK] Зависимости установлены"

# Запуск приложения
echo ""
echo "========================================"
echo "  Запуск сервера..."
echo "========================================"
echo ""
echo "Откройте в браузере: http://localhost:8000"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""
echo "========================================"
echo ""

python3 app.py

