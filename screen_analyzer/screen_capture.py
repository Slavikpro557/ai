import cv2
import numpy as np
import mss
import pyautogui
from typing import List, Tuple, Optional, Dict
from PIL import Image
from game.durak_game import Card

class ScreenAnalyzer:
    def __init__(self):
        self.sct = mss.mss()
        self.card_templates = self._load_card_templates()
        self.button_templates = self._load_button_templates()
        self.game_region = None
        self.card_positions: Dict[str, Tuple[int, int]] = {}  # Кэш позиций карт
        
    def _load_card_templates(self) -> dict:
        # Здесь будет загрузка шаблонов карт
        # В реальном приложении нужно добавить шаблоны всех карт
        return {}
    
    def _load_button_templates(self) -> dict:
        # Загрузка шаблонов кнопок (Бито, Взять и т.д.)
        return {}
        
    def calibrate_game_region(self):
        """Определение области экрана с игрой"""
        print("Наведите курсор на верхний левый угол игрового поля и нажмите Enter")
        input()
        top_left = pyautogui.position()
        
        print("Наведите курсор на нижний правый угол игрового поля и нажмите Enter")
        input()
        bottom_right = pyautogui.position()
        
        self.game_region = {
            "top": top_left.y,
            "left": top_left.x,
            "width": bottom_right.x - top_left.x,
            "height": bottom_right.y - top_left.y
        }
        
    def capture_game_screen(self) -> np.ndarray:
        """Захват экрана игры"""
        if not self.game_region:
            raise ValueError("Необходимо сначала откалибровать область игры")
        
        screenshot = self.sct.grab(self.game_region)
        return np.array(screenshot)
    
    def detect_table_cards(self, screen: np.ndarray) -> List[Card]:
        """Определение карт на столе"""
        # Определяем область стола (центральная часть экрана)
        height, width = screen.shape[:2]
        table_region = screen[height//4:3*height//4, width//4:3*width//4]
        
        detected_cards = []
        gray = cv2.cvtColor(table_region, cv2.COLOR_BGR2GRAY)
        
        for card_name, template in self.card_templates.items():
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            
            for pt in zip(*locations[::-1]):
                suit, rank = self._parse_card_name(card_name)
                card = Card(suit, rank)
                if card not in detected_cards:  # Избегаем дубликатов
                    detected_cards.append(card)
        
        return detected_cards
    
    def detect_cards(self, screen: np.ndarray) -> List[Tuple[Card, Tuple[int, int]]]:
        """Определение карт в руке игрока и их позиций"""
        # Определяем область руки игрока (нижняя часть экрана)
        height, width = screen.shape[:2]
        hand_region = screen[3*height//4:, :]
        
        detected_cards = []
        gray = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
        
        for card_name, template in self.card_templates.items():
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            
            for pt in zip(*locations[::-1]):
                suit, rank = self._parse_card_name(card_name)
                card = Card(suit, rank)
                # Преобразуем координаты относительно всего экрана
                screen_pt = (pt[0], pt[1] + 3*height//4)
                detected_cards.append((card, screen_pt))
                # Сохраняем позицию карты в кэше
                self.card_positions[str(card)] = screen_pt
        
        return detected_cards
    
    def count_opponent_cards(self, screen: np.ndarray) -> int:
        """Подсчет количества карт у противника"""
        # Определяем область карт противника (верхняя часть экрана)
        height = screen.shape[0]
        opponent_region = screen[:height//4, :]
        
        # Используем шаблон рубашки карты для подсчета
        if 'card_back' in self.card_templates:
            gray = cv2.cvtColor(opponent_region, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray, self.card_templates['card_back'], cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            return len(list(zip(*locations[::-1])))
        
        return 0  # Если не удалось определить
    
    def count_deck_cards(self, screen: np.ndarray) -> int:
        """Определение количества карт в колоде"""
        # Определяем область колоды (правая часть экрана)
        height, width = screen.shape[:2]
        deck_region = screen[:, 3*width//4:]
        
        # Используем шаблон рубашки карты
        if 'card_back' in self.card_templates:
            gray = cv2.cvtColor(deck_region, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray, self.card_templates['card_back'], cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            return len(list(zip(*locations[::-1])))
        
        return 0  # Если не удалось определить
    
    def find_card_position(self, card: Card) -> Optional[Tuple[int, int]]:
        """Находит позицию конкретной карты на экране"""
        card_key = str(card)
        if card_key in self.card_positions:
            return self.card_positions[card_key]
        return None
    
    def find_take_button(self) -> Optional[Tuple[int, int]]:
        """Находит кнопку 'Взять'"""
        if 'take_button' in self.button_templates:
            screen = self.capture_game_screen()
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray, self.button_templates['take_button'], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= 0.8:
                return max_loc
        return None
    
    def find_done_button(self) -> Optional[Tuple[int, int]]:
        """Находит кнопку 'Бито'"""
        if 'done_button' in self.button_templates:
            screen = self.capture_game_screen()
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray, self.button_templates['done_button'], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= 0.8:
                return max_loc
        return None
    
    def _parse_card_name(self, card_name: str) -> Tuple[str, str]:
        """Парсинг имени карты на масть и ранг"""
        # Пример: "hearts_ace" -> ("♥", "A")
        suit_map = {"hearts": "♥", "diamonds": "♦", "clubs": "♣", "spades": "♠"}
        rank_map = {
            "ace": "A", "king": "K", "queen": "Q", "jack": "J",
            "10": "10", "9": "9", "8": "8", "7": "7", "6": "6"
        }
        
        suit, rank = card_name.split("_")
        return suit_map[suit], rank_map[rank] 