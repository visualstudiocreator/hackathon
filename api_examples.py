"""
Примеры использования API анализатора сценариев
"""

from screenplay_processor import ScreenplayProcessor
import json


def example_1_basic_processing():
    """Пример 1: Базовая обработка сценария"""
    print("\n=== Пример 1: Базовая обработка ===\n")
    
    processor = ScreenplayProcessor()
    
    # Обрабатываем сценарий с базовым пресетом
    result = processor.process_screenplay(
        file_path='example_screenplay.docx',  # Замените на ваш файл
        preset='basic',
        export_format='xlsx'
    )
    
    if result['success']:
        print(f"✓ Успешно обработано!")
        print(f"  Сцен: {result['scenes_count']}")
        print(f"  Страниц: {result['pages']}")
        print(f"  Время: {result['processing_time']} сек")
        print(f"  Файл: {result['output_file']}")
    else:
        print(f"✗ Ошибка: {result['error']}")


def example_2_extended_processing():
    """Пример 2: Расширенная обработка с XLSX"""
    print("\n=== Пример 2: Расширенная обработка ===\n")
    
    processor = ScreenplayProcessor()
    
    result = processor.process_screenplay(
        file_path='example_screenplay.pdf',  # Замените на ваш файл
        preset='extended',
        export_format='xlsx',
        output_filename='my_preproduction'
    )
    
    if result['success']:
        print(f"✓ Обработка завершена")
        print(f"  Основной файл: {result['output_file']}")
        print(f"  Статистика: {result['summary_file']}")
        print(f"\nИнформация о сценарии:")
        print(f"  - Количество сцен: {result['scenes_count']}")
        print(f"  - Страниц: {result['pages']}")
        print(f"  - Кодировка: {result['encoding']}")


def example_3_custom_columns():
    """Пример 3: Использование пользовательских колонок"""
    print("\n=== Пример 3: Пользовательские колонки ===\n")
    
    processor = ScreenplayProcessor()
    
    # Определяем свой набор колонок
    custom_columns = [
        'Номер сцены',
        'Локация',
        'Время суток',
        'Персонажи',
        'Транспорт',
        'Оружие',
        'Спецэффекты',
        'Краткое описание'
    ]
    
    # Валидируем колонки
    is_valid, error = processor.validate_custom_columns(custom_columns)
    
    if not is_valid:
        print(f"✗ Некорректные колонки: {error}")
        return
    
    print("✓ Колонки валидны")
    
    # Обрабатываем с пользовательскими колонками
    result = processor.process_screenplay(
        file_path='example_screenplay.docx',
        custom_columns=custom_columns,
        export_format='xlsx'
    )
    
    if result['success']:
        print(f"✓ Файл создан: {result['output_file']}")


def example_4_preview():
    """Пример 4: Быстрое превью без полной обработки"""
    print("\n=== Пример 4: Превью сценария ===\n")
    
    processor = ScreenplayProcessor()
    
    # Получаем превью первых 3 сцен
    preview = processor.get_scenes_preview(
        file_path='example_screenplay.docx',
        num_scenes=3
    )
    
    if preview['success']:
        print(f"Информация о сценарии:")
        print(f"  Всего сцен: {preview['total_scenes']}")
        print(f"  Страниц: {preview['pages']}")
        print(f"\nПревью первых сцен:")
        
        for i, scene in enumerate(preview['preview_scenes'], 1):
            print(f"\n--- Сцена {scene['scene_number']} ---")
            print(f"Заголовок: {scene['header']}")
            print(f"Локация: {scene.get('location', 'Не определена')}")
            print(f"Время: {scene.get('time_of_day', 'Не определено')}")
            print(f"Слов: {scene.get('word_count', 0)}")
    else:
        print(f"✗ Ошибка: {preview['error']}")


def example_5_all_presets():
    """Пример 5: Обработка со всеми пресетами"""
    print("\n=== Пример 5: Все пресеты ===\n")
    
    processor = ScreenplayProcessor()
    
    # Получаем все доступные пресеты
    presets = processor.get_available_presets()
    
    print("Доступные пресеты:")
    for preset_key, preset_data in presets.items():
        print(f"\n{preset_key.upper()}:")
        print(f"  Название: {preset_data['name']}")
        print(f"  Колонок: {len(preset_data['columns'])}")
        print(f"  Первые колонки: {', '.join(preset_data['columns'][:3])}...")


def example_6_batch_processing():
    """Пример 6: Пакетная обработка нескольких файлов"""
    print("\n=== Пример 6: Пакетная обработка ===\n")
    
    processor = ScreenplayProcessor()
    
    files = [
        'screenplay1.docx',
        'screenplay2.pdf',
        'screenplay3.docx'
    ]
    
    results = []
    
    for file_path in files:
        print(f"\nОбработка: {file_path}")
        
        result = processor.process_screenplay(
            file_path=file_path,
            preset='extended',
            export_format='xlsx'
        )
        
        if result['success']:
            print(f"  ✓ Сцен: {result['scenes_count']}, Время: {result['processing_time']}с")
            results.append(result)
        else:
            print(f"  ✗ Ошибка: {result['error']}")
    
    print(f"\n\nУспешно обработано: {len(results)} из {len(files)}")


def example_7_csv_export():
    """Пример 7: Экспорт в CSV"""
    print("\n=== Пример 7: Экспорт в CSV ===\n")
    
    processor = ScreenplayProcessor()
    
    result = processor.process_screenplay(
        file_path='example_screenplay.docx',
        preset='extended',
        export_format='csv'  # CSV вместо XLSX
    )
    
    if result['success']:
        print(f"✓ CSV файл создан: {result['output_file']}")
        print(f"  Можно открыть в Excel, Google Sheets и других программах")


def example_8_available_columns():
    """Пример 8: Получение списка всех доступных колонок"""
    print("\n=== Пример 8: Доступные колонки ===\n")
    
    processor = ScreenplayProcessor()
    
    columns = processor.get_available_columns()
    
    print(f"Всего доступно {len(columns)} колонок:\n")
    for i, column in enumerate(columns, 1):
        print(f"{i:2}. {column}")


def example_9_scene_analysis():
    """Пример 9: Детальный анализ отдельных сцен"""
    print("\n=== Пример 9: Анализ отдельных сцен ===\n")
    
    from document_parser import DocumentParser
    from scene_segmenter import SceneSegmenter
    from nlp_analyzer import NLPAnalyzer
    
    # Парсим документ
    parser = DocumentParser()
    text, metadata = parser.parse('example_screenplay.docx')
    
    # Сегментируем на сцены
    segmenter = SceneSegmenter()
    scenes = segmenter.segment(text)
    
    # Анализируем первую сцену детально
    analyzer = NLPAnalyzer()
    scene = analyzer.analyze_scene(scenes[0])
    
    print(f"Сцена {scene['scene_number']}:")
    print(f"  Локация: {scene['location']}")
    print(f"  Время: {scene['time_of_day']}")
    print(f"  Интерьер/Экстерьер: {scene['interior_exterior']}")
    print(f"  Персонажи: {', '.join(scene['characters'][:5])}")
    print(f"  Реквизит: {', '.join(scene['props'][:5])}")
    print(f"  Транспорт: {', '.join(scene['transport'])}")
    print(f"  Спецэффекты: {', '.join(scene['sfx'])}")
    print(f"  Описание: {scene['description'][:100]}...")


def main():
    """Запуск всех примеров"""
    print("=" * 60)
    print(" ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ API АНАЛИЗАТОРА СЦЕНАРИЕВ")
    print("=" * 60)
    
    examples = [
        ("Базовая обработка", example_1_basic_processing),
        ("Расширенная обработка", example_2_extended_processing),
        ("Пользовательские колонки", example_3_custom_columns),
        ("Превью сценария", example_4_preview),
        ("Все пресеты", example_5_all_presets),
        ("Пакетная обработка", example_6_batch_processing),
        ("Экспорт в CSV", example_7_csv_export),
        ("Доступные колонки", example_8_available_columns),
        ("Анализ отдельных сцен", example_9_scene_analysis),
    ]
    
    print("\nДоступные примеры:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\n0. Запустить все примеры")
    print("q. Выход")
    
    while True:
        choice = input("\nВыберите пример (или 'q' для выхода): ").strip()
        
        if choice.lower() == 'q':
            print("\nДо свидания!")
            break
        
        if choice == '0':
            for name, example_func in examples:
                try:
                    example_func()
                except Exception as e:
                    print(f"✗ Ошибка в примере '{name}': {e}")
                input("\nНажмите Enter для продолжения...")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    name, example_func = examples[idx]
                    try:
                        example_func()
                    except Exception as e:
                        print(f"✗ Ошибка: {e}")
                    input("\nНажмите Enter для продолжения...")
                else:
                    print("Некорректный номер примера")
            except ValueError:
                print("Введите число или 'q'")


if __name__ == '__main__':
    main()

