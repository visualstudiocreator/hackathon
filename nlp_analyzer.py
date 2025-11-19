"""
NLP-анализатор для извлечения производственных элементов из сценария
Использует локальные модели без обращения к внешним API
"""

import re
from typing import List, Dict, Set
from collections import defaultdict
import pymorphy3
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsNERTagger,
    Doc,
    NamesExtractor
)
import config


class NLPAnalyzer:
    """Анализатор для извлечения сущностей из текста сценария"""
    
    def __init__(self):
        # Инициализируем компоненты Natasha для русского языка
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)
        self.names_extractor = NamesExtractor(self.morph_vocab)
        
        # PyMorphy для морфологического анализа
        self.morph = pymorphy3.MorphAnalyzer()
        
        # Загружаем ключевые слова из конфига
        self.keywords = config.KEYWORDS
        
        # Кэш для персонажей
        self.character_cache = set()
    
    def analyze_scene(self, scene: Dict) -> Dict:
        """
        Анализирует сцену и извлекает все производственные элементы
        
        Args:
            scene: словарь со сценой
            
        Returns:
            Dict: обогащенный словарь с извлеченными элементами
        """
        text = scene.get('text', '')
        
        # Базовая информация уже есть в scene
        result = scene.copy()
        
        # Извлекаем персонажей
        result['characters'] = self._extract_characters(text)
        result['main_characters'] = result['characters'][:5]  # Первые 5 как основные
        result['secondary_characters'] = result['characters'][5:]  # Остальные как второстепенные
        
        # Извлекаем массовку
        result['extras'] = self._extract_extras(text)
        
        # Извлекаем реквизит
        result['props'] = self._extract_props(text)
        
        # Извлекаем транспорт
        result['transport'] = self._extract_transport(text)
        
        # Извлекаем животных
        result['animals'] = self._extract_animals(text)
        
        # Извлекаем спецэффекты
        result['sfx'] = self._extract_sfx(text)
        
        # Извлекаем информацию о гриме и костюмах
        result['makeup'] = self._extract_makeup(text)
        
        # Извлекаем каскадерские трюки
        result['stunts'] = self._extract_stunts(text)
        
        # Извлекаем музыку и звуки
        result['music'] = self._extract_music(text)
        
        # Извлекаем оружие
        result['weapons'] = self._extract_weapons(text)
        
        # Извлекаем еду и напитки
        result['food'] = self._extract_food(text)
        
        # Если локация не была извлечена ранее, пытаемся извлечь её
        if not result.get('location'):
            result['location'] = self._extract_location(text)
        
        # Если время суток не было извлечено, пытаемся извлечь
        if not result.get('time_of_day'):
            result['time_of_day'] = self._extract_time_of_day(text)
        
        # Если интерьер/экстерьер не был определен, пытаемся определить
        if not result.get('interior_exterior'):
            result['interior_exterior'] = self._extract_interior_exterior(text)
        
        # Создаем краткое описание (первые 2-3 предложения)
        result['description'] = self._create_description(text)
        
        return result
    
    def _extract_characters(self, text: str) -> List[str]:
        """Извлекает имена персонажей из текста"""
        characters = set()
        
        # Используем NER для извлечения имен
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)
        
        for span in doc.spans:
            if span.type == 'PER':  # Персона
                name = span.text
                # Нормализуем имя
                name_normalized = self._normalize_name(name)
                if name_normalized:
                    characters.add(name_normalized)
                    self.character_cache.add(name_normalized)
        
        # Также ищем имена в диалогах (обычно пишутся заглавными буквами)
        # Формат: "ИВАН:" или "ИВАН (улыбаясь)"
        dialogue_pattern = r'^([А-ЯЁ][А-ЯЁ\s]+)(?:\s*\(|:)'
        for line in text.split('\n'):
            match = re.search(dialogue_pattern, line.strip(), re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name.split()) <= 3:  # Максимум 3 слова в имени
                    name_normalized = self._normalize_name(name)
                    if name_normalized:
                        characters.add(name_normalized)
                        self.character_cache.add(name_normalized)
        
        return sorted(list(characters))
    
    def _normalize_name(self, name: str) -> str:
        """Нормализует имя персонажа"""
        # Удаляем лишние пробелы
        name = ' '.join(name.split())
        
        # Проверяем, что это действительно похоже на имя
        words = name.split()
        if len(words) > 3:
            return ''
        
        # Проверяем, что не является служебным словом
        stop_words = {'КАДР', 'СЦЕНА', 'КОНЕЦ', 'ТИТРЫ', 'ФОН', 'ГОЛОС'}
        if name.upper() in stop_words:
            return ''
        
        return name.title()
    
    def _extract_extras(self, text: str) -> List[str]:
        """Извлекает упоминания массовки"""
        extras = []
        text_lower = text.lower()
        
        for keyword in self.keywords['crowd']:
            if keyword in text_lower:
                # Ищем контекст вокруг ключевого слова
                pattern = r'([^.!?]*' + re.escape(keyword) + r'[^.!?]*[.!?])'
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    extras.append(match.strip())
        
        return list(set(extras))
    
    def _extract_props(self, text: str) -> List[str]:
        """Извлекает реквизит из текста"""
        props = set()
        
        # Список общих предметов реквизита
        prop_keywords = [
            'стол', 'стул', 'кресло', 'диван', 'шкаф', 'зеркало',
            'телефон', 'компьютер', 'ноутбук', 'телевизор',
            'книга', 'газета', 'журнал', 'документ', 'письмо',
            'сумка', 'чемодан', 'рюкзак', 'портфель',
            'ключи', 'кошелек', 'часы', 'очки',
            'фотография', 'картина', 'портрет',
            'бутылка', 'стакан', 'чашка', 'тарелка',
            'цветы', 'букет', 'растение',
            'лампа', 'свеча', 'фонарь',
            'мяч', 'игрушка'
        ]
        
        text_lower = text.lower()
        
        for prop_word in prop_keywords:
            if prop_word in text_lower:
                props.add(prop_word.capitalize())
        
        return sorted(list(props))
    
    def _extract_transport(self, text: str) -> List[str]:
        """Извлекает транспортные средства"""
        vehicles = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['vehicles']:
            if keyword in text_lower:
                vehicles.add(keyword.capitalize())
        
        return sorted(list(vehicles))
    
    def _extract_animals(self, text: str) -> List[str]:
        """Извлекает упоминания животных"""
        animals = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['animals']:
            if keyword in text_lower:
                animals.add(keyword.capitalize())
        
        return sorted(list(animals))
    
    def _extract_sfx(self, text: str) -> List[str]:
        """Извлекает спецэффекты"""
        sfx = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['sfx']:
            if keyword in text_lower:
                sfx.add(keyword.capitalize())
        
        return sorted(list(sfx))
    
    def _extract_makeup(self, text: str) -> List[str]:
        """Извлекает информацию о гриме и костюмах"""
        makeup = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['makeup']:
            if keyword in text_lower:
                makeup.add(keyword.capitalize())
        
        return sorted(list(makeup))
    
    def _extract_stunts(self, text: str) -> List[str]:
        """Извлекает каскадерские элементы"""
        stunts = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['stunts']:
            if keyword in text_lower:
                stunts.add(keyword.capitalize())
        
        return sorted(list(stunts))
    
    def _extract_music(self, text: str) -> List[str]:
        """Извлекает музыкальные элементы"""
        music = []
        text_lower = text.lower()
        
        music_keywords = ['музыка', 'песня', 'мелодия', 'звучит', 'играет',
                         'гитара', 'пианино', 'скрипка', 'барабан', 'инструмент']
        
        for keyword in music_keywords:
            if keyword in text_lower:
                music.append(keyword.capitalize())
        
        return list(set(music))
    
    def _extract_weapons(self, text: str) -> List[str]:
        """Извлекает оружие"""
        weapons = set()
        text_lower = text.lower()
        
        for keyword in self.keywords['weapons']:
            if keyword in text_lower:
                weapons.add(keyword.capitalize())
        
        return sorted(list(weapons))
    
    def _extract_food(self, text: str) -> List[str]:
        """Извлекает еду и напитки"""
        food = []
        text_lower = text.lower()
        
        food_keywords = ['кофе', 'чай', 'вино', 'пиво', 'вода', 'сок',
                        'хлеб', 'суп', 'салат', 'мясо', 'рыба',
                        'торт', 'пирог', 'конфета', 'шоколад',
                        'завтрак', 'обед', 'ужин', 'еда', 'блюдо']
        
        for keyword in food_keywords:
            if keyword in text_lower:
                food.append(keyword.capitalize())
        
        return list(set(food))
    
    def _extract_location(self, text: str) -> str:
        """Извлекает локацию из текста"""
        # Ищем упоминания мест в первых строках
        lines = text.split('\n')[:5]
        
        location_keywords = ['кухня', 'гостиная', 'спальня', 'кабинет', 'офис',
                           'улица', 'парк', 'площадь', 'кафе', 'ресторан',
                           'магазин', 'больница', 'школа', 'квартира', 'дом']
        
        for line in lines:
            line_lower = line.lower()
            for keyword in location_keywords:
                if keyword in line_lower:
                    return keyword.capitalize()
        
        return ''
    
    def _extract_time_of_day(self, text: str) -> str:
        """Извлекает время суток из текста"""
        text_lower = text.lower()
        
        for keyword_list, value in [
            (self.keywords['time_day'], 'День'),
            (self.keywords['time_night'], 'Ночь'),
            (self.keywords['time_morning'], 'Утро'),
            (self.keywords['time_evening'], 'Вечер')
        ]:
            for keyword in keyword_list:
                if keyword in text_lower:
                    return value
        
        return ''
    
    def _extract_interior_exterior(self, text: str) -> str:
        """Определяет интерьер или экстерьер"""
        text_lower = text.lower()
        
        interior_count = sum(1 for keyword in self.keywords['interior'] if keyword in text_lower)
        exterior_count = sum(1 for keyword in self.keywords['exterior'] if keyword in text_lower)
        
        if interior_count > exterior_count:
            return 'Интерьер'
        elif exterior_count > interior_count:
            return 'Экстерьер'
        
        return ''
    
    def _create_description(self, text: str) -> str:
        """Создает краткое описание сцены"""
        # Берем первые 2-3 предложения или первые 200 символов
        sentences = re.split(r'[.!?]+', text)
        
        description_parts = []
        char_count = 0
        
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence and char_count < 200:
                description_parts.append(sentence)
                char_count += len(sentence)
        
        description = '. '.join(description_parts)
        
        if len(description) > 200:
            description = description[:197] + '...'
        
        return description
    
    def batch_analyze_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Анализирует несколько сцен
        
        Args:
            scenes: список сцен
            
        Returns:
            List[Dict]: список проанализированных сцен
        """
        analyzed_scenes = []
        
        for scene in scenes:
            analyzed_scene = self.analyze_scene(scene)
            analyzed_scenes.append(analyzed_scene)
        
        return analyzed_scenes

