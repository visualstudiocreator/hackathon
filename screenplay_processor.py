"""
Основной модуль обработки сценариев
Координирует работу всех компонентов системы
"""

import os
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from document_parser import DocumentParser
from scene_segmenter import SceneSegmenter
from nlp_analyzer import NLPAnalyzer
from data_exporter import DataExporter
import config


class ScreenplayProcessor:
    """Главный класс для обработки сценариев"""
    
    def __init__(self):
        self.parser = DocumentParser()
        self.segmenter = SceneSegmenter()
        self.analyzer = NLPAnalyzer()
        self.exporter = DataExporter()
        
        # Создаем необходимые директории
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    
    def process_screenplay(
        self,
        file_path: str,
        preset: str = 'extended',
        custom_columns: Optional[List[str]] = None,
        export_format: str = 'xlsx',
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        Обрабатывает сценарий от начала до конца
        
        Args:
            file_path: путь к файлу сценария
            preset: название пресета ('basic', 'extended', 'full')
            custom_columns: пользовательские колонки (если preset не используется)
            export_format: формат экспорта ('csv' или 'xlsx')
            output_filename: имя выходного файла
            
        Returns:
            Dict: результаты обработки
        """
        start_time = time.time()
        
        try:
            # 1. Валидация файла
            is_valid, error_msg = self.parser.validate_file(file_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # 2. Парсинг документа
            print("Парсинг документа...")
            text, metadata = self.parser.parse(file_path)
            
            if not text or len(text.strip()) < 100:
                return {
                    'success': False,
                    'error': 'Не удалось извлечь текст из документа или текст слишком короткий'
                }
            
            print(f"Извлечено {len(text)} символов, {metadata['pages']} страниц")
            
            # 3. Сегментация на сцены
            print("Сегментация на сцены...")
            scenes = self.segmenter.segment(text)
            print(f"Найдено {len(scenes)} сцен")
            
            if not scenes:
                return {
                    'success': False,
                    'error': 'Не удалось разделить сценарий на сцены'
                }
            
            # 4. NLP-анализ каждой сцены
            print("Анализ сцен...")
            analyzed_scenes = self.analyzer.batch_analyze_scenes(scenes)
            print("Анализ завершен")
            
            # 5. Определяем колонки для экспорта
            if custom_columns:
                columns = custom_columns
            else:
                columns = config.PRESETS.get(preset, config.PRESETS['extended'])['columns']
            
            # 6. Экспорт данных
            print(f"Экспорт в формат {export_format}...")
            output_path = self.exporter.export(
                analyzed_scenes,
                columns,
                format=export_format,
                filename=output_filename
            )
            
            # 7. Экспорт сводной статистики
            summary_path = self.exporter.export_summary(
                analyzed_scenes,
                filename=output_filename.replace(f'.{export_format}', '_summary.xlsx') if output_filename else None
            )
            
            # Вычисляем время обработки
            processing_time = time.time() - start_time
            
            # Проверяем ограничение по времени
            if processing_time > config.MAX_PROCESSING_TIME_MINUTES * 60:
                print(f"Предупреждение: обработка заняла {processing_time/60:.1f} минут, "
                      f"что превышает лимит в {config.MAX_PROCESSING_TIME_MINUTES} минут")
            
            return {
                'success': True,
                'scenes_count': len(analyzed_scenes),
                'pages': metadata['pages'],
                'encoding': metadata['encoding'],
                'processing_time': round(processing_time, 2),
                'output_file': output_path,
                'summary_file': summary_path,
                'scenes': analyzed_scenes
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_presets(self) -> Dict:
        """Возвращает доступные пресеты"""
        return config.PRESETS
    
    def get_available_columns(self) -> List[str]:
        """Возвращает все доступные колонки"""
        all_columns = set()
        
        for preset in config.PRESETS.values():
            all_columns.update(preset['columns'])
        
        return sorted(list(all_columns))
    
    def validate_custom_columns(self, columns: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Валидирует пользовательские колонки
        
        Args:
            columns: список колонок
            
        Returns:
            Tuple[bool, Optional[str]]: (валидны ли колонки, сообщение об ошибке)
        """
        if not columns:
            return False, "Список колонок не может быть пустым"
        
        available_columns = self.get_available_columns()
        
        invalid_columns = [col for col in columns if col not in available_columns]
        
        if invalid_columns:
            return False, f"Неизвестные колонки: {', '.join(invalid_columns)}"
        
        return True, None
    
    def get_scenes_preview(self, file_path: str, num_scenes: int = 3) -> Dict:
        """
        Возвращает превью первых нескольких сцен без полного анализа
        
        Args:
            file_path: путь к файлу
            num_scenes: количество сцен для превью
            
        Returns:
            Dict: превью сцен
        """
        try:
            # Валидация
            is_valid, error_msg = self.parser.validate_file(file_path)
            if not is_valid:
                return {'success': False, 'error': error_msg}
            
            # Парсинг
            text, metadata = self.parser.parse(file_path)
            
            # Сегментация
            scenes = self.segmenter.segment(text)
            
            # Возвращаем первые N сцен
            preview_scenes = scenes[:num_scenes]
            
            return {
                'success': True,
                'total_scenes': len(scenes),
                'pages': metadata['pages'],
                'preview_scenes': preview_scenes
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    """Пример использования процессора"""
    processor = ScreenplayProcessor()
    
    # Пример обработки файла
    file_path = 'example_screenplay.docx'
    
    if os.path.exists(file_path):
        print(f"Обработка файла: {file_path}")
        
        result = processor.process_screenplay(
            file_path=file_path,
            preset='extended',
            export_format='xlsx'
        )
        
        if result['success']:
            print(f"\nУспешно обработано!")
            print(f"Количество сцен: {result['scenes_count']}")
            print(f"Страниц: {result['pages']}")
            print(f"Время обработки: {result['processing_time']} сек")
            print(f"Результат сохранен в: {result['output_file']}")
            print(f"Статистика сохранена в: {result['summary_file']}")
        else:
            print(f"\nОшибка: {result['error']}")
    else:
        print(f"Файл {file_path} не найден")
        print("\nДоступные пресеты:")
        for preset_name, preset_data in processor.get_available_presets().items():
            print(f"  - {preset_name}: {preset_data['name']}")
            print(f"    Колонки: {', '.join(preset_data['columns'][:3])}...")


if __name__ == '__main__':
    main()

