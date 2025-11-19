"""
Модуль для сегментации сценария на отдельные сцены
"""

import re
from typing import List, Dict
from razdel import sentenize


class SceneSegmenter:
    """Сегментатор для разделения сценария на сцены"""
    
    def __init__(self):
        # Регулярные выражения для определения начала сцены
        self.scene_patterns = [
            # Формат: "СЦЕНА 1", "Сцена 1", "Сц. 1"
            r'(?:СЦЕНА|Сцена|сцена|СЦ\.|Сц\.)\s*(\d+)',
            
            # Формат: "1. ИНТЕРЬЕР. КУХНЯ - ДЕНЬ"
            r'^(\d+)\.\s*(?:ИНТЕРЬЕР|ЭКСТЕРЬЕР|ИНТ\.|ЭКС\.)',
            
            # Формат: "№1", "# 1"
            r'(?:№|#)\s*(\d+)',
            
            # Формат: "INT. KITCHEN - DAY" (англоязычный формат)
            r'^(?:INT\.|EXT\.)\s+[A-ZА-ЯЁ\s]+-\s*(?:DAY|NIGHT|MORNING|EVENING|ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР)',
        ]
        
        # Паттерны для определения локации и времени
        self.location_time_pattern = r'(?:ИНТЕРЬЕР|ЭКСТЕРЬЕР|ИНТ\.|ЭКС\.|INT\.|EXT\.)\s+([^-\n]+)\s*-\s*([^\n]+)'
    
    def segment(self, text: str) -> List[Dict]:
        """
        Разделяет текст сценария на сцены
        
        Args:
            text: текст сценария
            
        Returns:
            List[Dict]: список сцен с метаданными
        """
        scenes = []
        lines = text.split('\n')
        
        current_scene = None
        current_scene_number = 0
        current_scene_lines = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Пропускаем пустые строки
            if not line_stripped:
                if current_scene_lines:
                    current_scene_lines.append(line)
                continue
            
            # Проверяем, является ли строка началом новой сцены
            scene_match = self._is_scene_header(line_stripped)
            
            if scene_match:
                # Сохраняем предыдущую сцену
                if current_scene is not None and current_scene_lines:
                    current_scene['text'] = '\n'.join(current_scene_lines).strip()
                    current_scene['word_count'] = len(current_scene['text'].split())
                    scenes.append(current_scene)
                
                # Начинаем новую сцену
                current_scene_number += 1
                scene_number = scene_match.get('number', current_scene_number)
                
                current_scene = {
                    'scene_number': scene_number,
                    'header': line_stripped,
                    'line_start': i + 1,
                    'location': scene_match.get('location', ''),
                    'time_of_day': scene_match.get('time_of_day', ''),
                    'interior_exterior': scene_match.get('int_ext', ''),
                }
                
                current_scene_lines = [line]
            else:
                # Добавляем строку к текущей сцене
                if current_scene is not None:
                    current_scene_lines.append(line)
        
        # Сохраняем последнюю сцену
        if current_scene is not None and current_scene_lines:
            current_scene['text'] = '\n'.join(current_scene_lines).strip()
            current_scene['word_count'] = len(current_scene['text'].split())
            scenes.append(current_scene)
        
        # Если не найдено ни одной сцены, создаем одну сцену из всего текста
        if not scenes:
            scenes = self._create_default_scenes(text)
        
        return scenes
    
    def _is_scene_header(self, line: str) -> Dict:
        """
        Проверяет, является ли строка заголовком сцены
        
        Args:
            line: строка для проверки
            
        Returns:
            Dict: словарь с информацией о сцене или None
        """
        line_upper = line.upper()
        
        # Проверяем каждый паттерн
        for pattern in self.scene_patterns:
            match = re.search(pattern, line, re.IGNORECASE | re.MULTILINE)
            if match:
                result = {
                    'number': int(match.group(1)) if match.groups() else None,
                    'location': '',
                    'time_of_day': '',
                    'int_ext': ''
                }
                
                # Пытаемся извлечь локацию и время
                loc_time_match = re.search(self.location_time_pattern, line, re.IGNORECASE)
                if loc_time_match:
                    result['location'] = loc_time_match.group(1).strip()
                    result['time_of_day'] = loc_time_match.group(2).strip()
                    
                    # Определяем интерьер/экстерьер
                    if 'ИНТЕРЬЕР' in line_upper or 'ИНТ.' in line_upper or 'INT.' in line_upper:
                        result['int_ext'] = 'Интерьер'
                    elif 'ЭКСТЕРЬЕР' in line_upper or 'ЭКС.' in line_upper or 'EXT.' in line_upper:
                        result['int_ext'] = 'Экстерьер'
                
                return result
        
        # Проверяем, содержит ли строка ключевые слова локации и времени
        if self._looks_like_scene_header(line_upper):
            return {
                'number': None,
                'location': self._extract_location(line),
                'time_of_day': self._extract_time_of_day(line),
                'int_ext': self._extract_int_ext(line)
            }
        
        return None
    
    def _looks_like_scene_header(self, line: str) -> bool:
        """Проверяет, похожа ли строка на заголовок сцены"""
        keywords = ['ИНТЕРЬЕР', 'ЭКСТЕРЬЕР', 'ИНТ.', 'ЭКС.', 'INT.', 'EXT.',
                   'ДЕНЬ', 'НОЧЬ', 'УТРО', 'ВЕЧЕР', 'DAY', 'NIGHT']
        
        # Короткая строка в верхнем регистре с ключевыми словами
        if len(line.split()) <= 10 and line.isupper():
            return any(keyword in line for keyword in keywords)
        
        return False
    
    def _extract_location(self, line: str) -> str:
        """Извлекает локацию из строки"""
        # Убираем префиксы
        line = re.sub(r'(?:ИНТЕРЬЕР|ЭКСТЕРЬЕР|ИНТ\.|ЭКС\.|INT\.|EXT\.)\s*[.:]?\s*', '', line, flags=re.IGNORECASE)
        
        # Берем текст до дефиса или до конца
        match = re.search(r'^([^-\n]+)', line)
        if match:
            return match.group(1).strip()
        
        return line.strip()
    
    def _extract_time_of_day(self, line: str) -> str:
        """Извлекает время суток из строки"""
        time_keywords = {
            'ДЕНЬ': 'День',
            'НОЧЬ': 'Ночь',
            'УТРО': 'Утро',
            'ВЕЧЕР': 'Вечер',
            'РАССВЕТ': 'Рассвет',
            'ЗАКАТ': 'Закат',
            'DAY': 'День',
            'NIGHT': 'Ночь',
            'MORNING': 'Утро',
            'EVENING': 'Вечер'
        }
        
        line_upper = line.upper()
        for keyword, value in time_keywords.items():
            if keyword in line_upper:
                return value
        
        return ''
    
    def _extract_int_ext(self, line: str) -> str:
        """Определяет интерьер/экстерьер"""
        line_upper = line.upper()
        
        if 'ИНТЕРЬЕР' in line_upper or 'ИНТ.' in line_upper or 'INT.' in line_upper:
            return 'Интерьер'
        elif 'ЭКСТЕРЬЕР' in line_upper or 'ЭКС.' in line_upper or 'EXT.' in line_upper:
            return 'Экстерьер'
        
        return ''
    
    def _create_default_scenes(self, text: str) -> List[Dict]:
        """
        Создает сцены по умолчанию, если не удалось распознать структуру
        
        Args:
            text: текст сценария
            
        Returns:
            List[Dict]: список сцен
        """
        # Разбиваем текст на параграфы
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        scenes = []
        scene_number = 1
        
        # Группируем параграфы по ~500 слов (примерно одна страница)
        current_scene_text = []
        current_word_count = 0
        
        for para in paragraphs:
            words = para.split()
            current_scene_text.append(para)
            current_word_count += len(words)
            
            # Создаем новую сцену каждые ~500 слов
            if current_word_count >= 500:
                scenes.append({
                    'scene_number': scene_number,
                    'header': f'Сцена {scene_number}',
                    'text': '\n\n'.join(current_scene_text),
                    'word_count': current_word_count,
                    'location': '',
                    'time_of_day': '',
                    'interior_exterior': '',
                    'line_start': 0
                })
                
                scene_number += 1
                current_scene_text = []
                current_word_count = 0
        
        # Добавляем последнюю сцену
        if current_scene_text:
            scenes.append({
                'scene_number': scene_number,
                'header': f'Сцена {scene_number}',
                'text': '\n\n'.join(current_scene_text),
                'word_count': current_word_count,
                'location': '',
                'time_of_day': '',
                'interior_exterior': '',
                'line_start': 0
            })
        
        return scenes

