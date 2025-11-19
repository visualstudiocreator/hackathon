"""
Тестовый скрипт для проверки экспорта с шаблоном
"""

import pandas as pd
from data_exporter import DataExporter

# Создаем тестовые данные
test_data = [
    {
        'scene_number': 1,
        'location': 'Квартира Ивана',
        'interior_exterior': 'Интерьер',
        'time_of_day': 'Утро',
        'characters': 'Иван',
        'main_characters': 'Иван',
        'secondary_characters': '',
        'extras': '',
        'props': 'Пистолет, телефон, блокнот',
        'transport': '',
        'animals': '',
        'sfx': '',
        'makeup': '',
        'stunts': '',
        'music': '',
        'weapons': 'Пистолет',
        'food': 'Виски',
        'description': 'Детектив сидит за столом и изучает фотографии'
    },
    {
        'scene_number': 2,
        'location': 'Улица города',
        'interior_exterior': 'Экстерьер',
        'time_of_day': 'Утро',
        'characters': 'Иван',
        'main_characters': 'Иван',
        'secondary_characters': '',
        'extras': 'Толпа прохожих',
        'props': '',
        'transport': 'Автомобиль',
        'animals': '',
        'sfx': '',
        'makeup': '',
        'stunts': '',
        'music': '',
        'weapons': '',
        'food': '',
        'description': 'Иван садится в машину и уезжает'
    }
]

# Создаем сцены с правильными ключами
scenes = []
for data in test_data:
    scene = {
        'scene_number': data['scene_number'],
        'location': data['location'],
        'interior_exterior': data['interior_exterior'],
        'time_of_day': data['time_of_day'],
        'characters': data['characters'].split(', ') if data['characters'] else [],
        'main_characters': data['main_characters'].split(', ') if data['main_characters'] else [],
        'secondary_characters': data['secondary_characters'].split(', ') if data['secondary_characters'] else [],
        'extras': data['extras'].split(', ') if data['extras'] else [],
        'props': data['props'].split(', ') if data['props'] else [],
        'transport': data['transport'].split(', ') if data['transport'] else [],
        'animals': data['animals'].split(', ') if data['animals'] else [],
        'sfx': data['sfx'].split(', ') if data['sfx'] else [],
        'makeup': data['makeup'].split(', ') if data['makeup'] else [],
        'stunts': data['stunts'].split(', ') if data['stunts'] else [],
        'music': data['music'].split(', ') if data['music'] else [],
        'weapons': data['weapons'].split(', ') if data['weapons'] else [],
        'food': data['food'].split(', ') if data['food'] else [],
        'description': data['description'],
        'word_count': len(data['description'].split())
    }
    scenes.append(scene)

# Экспортируем с использованием расширенного пресета
columns = [
    'Номер сцены',
    'Локация',
    'Внутри/Снаружи',
    'Время суток',
    'Персонажи',
    'Массовка',
    'Реквизит',
    'Транспорт',
    'Животные',
    'Спецэффекты',
    'Грим/Костюмы',
    'Каскадеры',
    'Оружие',
    'Еда/Напитки',
    'Краткое описание'
]

print("=" * 60)
print("ТЕСТ ЭКСПОРТА С ШАБЛОНОМ")
print("=" * 60)

exporter = DataExporter()

try:
    output_path = exporter.export(
        scenes=scenes,
        columns=columns,
        format='xlsx',
        filename='test_template_output'
    )
    
    print("\n" + "=" * 60)
    print("✓ УСПЕХ!")
    print(f"Файл создан: {output_path}")
    print("=" * 60)
    print("\nОткройте файл и проверьте:")
    print("1. Номер сцены должен быть в колонке 'Сцена'")
    print("2. Локация должна быть в колонке 'Объект'")
    print("3. Все данные в правильных колонках")
    print("4. Форматирование и стили сохранены")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("✗ ОШИБКА!")
    print(f"Ошибка: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()

