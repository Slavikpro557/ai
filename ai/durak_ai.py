from typing import List, Optional, Tuple
from game.durak_game import Card
from .learning_engine import LearningEngine, GameState, GameAction, GameResult
import random

class DurakAI:
    def __init__(self):
        self.hand: List[Card] = []
        self.known_cards: List[Card] = []
        self.trump_suit: Optional[str] = None
        self.opponent_cards_count = 0
        self.deck_remaining = 0
        self.aggressive_mode = True  # Режим агрессивной игры
        self.auto_play = False  # Режим автоматической игры
        
        # Добавляем систему обучения
        self.learning_engine = LearningEngine()
        self.current_game_moves = 0
        self.last_state = None
        self.last_action = None
    
    def update_game_state(self, hand: List[Card], trump_suit: str, 
                         opponent_cards: int = 0, deck_remaining: int = 0,
                         window_title: str = None):
        self.hand = hand
        self.trump_suit = trump_suit
        self.opponent_cards_count = opponent_cards
        self.deck_remaining = deck_remaining
        
        if window_title:
            self.learning_engine.detect_current_app(window_title)
    
    def set_auto_play(self, enabled: bool):
        """Включение/выключение режима автоматической игры"""
        self.auto_play = enabled
    
    def get_auto_play_action(self, table_cards: List[Card]) -> Tuple[str, Optional[Card]]:
        self.current_game_moves += 1
        
        # Создаем текущее состояние игры
        current_state = GameState(
            self.hand.copy(),
            table_cards.copy(),
            self.trump_suit,
            self.opponent_cards_count,
            self.deck_remaining
        )
        
        # Если был предыдущий ход, записываем его результат
        if self.last_state and self.last_action:
            result_score = self._evaluate_move_result(current_state)
            self.learning_engine.record_move(self.last_state, self.last_action, result_score)
        
        # Определяем действие
        action_type, card = self._choose_action(table_cards)
        
        # Сохраняем состояние и действие
        self.last_state = current_state
        self.last_action = GameAction(action_type, card)
        
        return action_type, card
    
    def _choose_action(self, table_cards: List[Card]) -> Tuple[str, Optional[Card]]:
        if not table_cards:
            card = self._choose_attack_card()
            return "attack", card
        elif len(table_cards) % 2 == 1:
            card = self._find_best_defense(table_cards[-1])
            if card:
                return "defend", card
            return "take", None
        else:
            card = self._choose_card_to_add(table_cards)
            if card:
                return "add", card
            return "done", None
    
    def _evaluate_move_result(self, current_state: GameState) -> float:
        """Оценка результата предыдущего хода"""
        score = 0.0
        
        # Изменение количества карт
        cards_diff = len(self.last_state.hand) - len(current_state.hand)
        if cards_diff > 0:  # Избавились от карт
            score += 0.3
        
        # Изменение у противника
        opponent_diff = current_state.opponent_cards - self.last_state.opponent_cards
        if opponent_diff > 0:  # Противник взял карты
            score += 0.4
        
        # Сохранение козырей
        prev_trumps = sum(1 for c in self.last_state.hand if c.suit == self.trump_suit)
        curr_trumps = sum(1 for c in current_state.hand if c.suit == self.trump_suit)
        if curr_trumps >= prev_trumps:
            score += 0.2
        
        return min(max(score, 0.0), 1.0)
    
    def end_game(self, won: bool):
        """Завершение игры и обучение"""
        if self.last_state and self.last_action:
            # Записываем последний ход
            result_score = 1.0 if won else 0.0
            self.learning_engine.record_move(self.last_state, self.last_action, result_score)
        
        # Обучаемся на результатах игры
        self.learning_engine.learn_from_game(GameResult(won, self.current_game_moves))
        
        # Сбрасываем счетчики
        self.current_game_moves = 0
        self.last_state = None
        self.last_action = None
    
    def _choose_attack_card(self) -> Optional[Card]:
        if not self.hand:
            return None
        
        # Получаем корректировки стратегии для текущего приложения
        adjustments = self.learning_engine.get_strategy_adjustments()
        
        # Оцениваем каждую карту для атаки
        scored_cards = []
        for card in self.hand:
            score = self._calculate_attack_score(card, adjustments)
            scored_cards.append((card, score))
        
        # Выбираем карту с лучшим счетом
        scored_cards.sort(key=lambda x: x[1], reverse=True)
        return scored_cards[0][0] if scored_cards else None
    
    def _calculate_attack_score(self, card: Card, adjustments: dict) -> float:
        weights = self.learning_engine.weights
        score = 0.0
        
        # Базовый счет по рангу с учетом корректировки
        rank_score = Card.RANKS.index(card.rank) / len(Card.RANKS)
        score += rank_score * weights["rank_weight"] * adjustments.get("rank_weight", 1.0)
        
        # Козырь или нет с учетом корректировки
        is_trump = card.suit == self.trump_suit
        if is_trump:
            if self.aggressive_mode:
                score -= weights["trump_weight"] * adjustments.get("trump_weight", 1.0)
            else:
                score += weights["trump_weight"] * adjustments.get("trump_weight", 1.0)
        
        # Учитываем количество карт у противника
        if self.opponent_cards_count <= 2:
            score += weights["opponent_cards_weight"]
        
        # Учитываем одинаковые значения карт
        same_rank_count = sum(1 for c in self.hand if c.rank == card.rank)
        score += same_rank_count * weights["same_rank_weight"]
        
        # Применяем фактор агрессивности
        score *= weights["aggressive_factor"] * adjustments.get("aggressive_factor", 1.0)
        
        return score
    
    def _find_best_defense(self, attacking_card: Card) -> Optional[Card]:
        possible_cards = [
            card for card in self.hand 
            if card.can_beat(attacking_card, self.trump_suit)
        ]
        
        if not possible_cards:
            return None
        
        adjustments = self.learning_engine.get_strategy_adjustments()
        scored_cards = []
        for card in possible_cards:
            score = self._calculate_defense_score(card, attacking_card, adjustments)
            scored_cards.append((card, score))
        
        scored_cards.sort(key=lambda x: x[1])
        return scored_cards[0][0] if scored_cards else None
    
    def _calculate_defense_score(self, card: Card, attacking_card: Card, 
                               adjustments: dict) -> float:
        weights = self.learning_engine.weights
        score = 0.0
        
        # Базовый счет по разнице в ранге
        rank_diff = Card.RANKS.index(card.rank) - Card.RANKS.index(attacking_card.rank)
        score += rank_diff * weights["rank_weight"] * adjustments.get("rank_weight", 1.0)
        
        # Козырь или нет
        if card.suit == self.trump_suit and attacking_card.suit != self.trump_suit:
            score += weights["trump_weight"] * adjustments.get("trump_weight", 1.0)
        
        # Учитываем количество оставшихся карт
        if len(self.hand) <= 3:
            score -= weights["opponent_cards_weight"]
        
        return score
    
    def _choose_card_to_add(self, table_cards: List[Card]) -> Optional[Card]:
        """Выбор карты для подкидывания"""
        if not table_cards:
            return None
        
        table_ranks = {card.rank for card in table_cards}
        possible_cards = [
            card for card in self.hand
            if card.rank in table_ranks
        ]
        
        if not possible_cards:
            return None
        
        adjustments = self.learning_engine.get_strategy_adjustments()
        scored_cards = []
        for card in possible_cards:
            score = self._calculate_attack_score(card, adjustments)
            scored_cards.append((card, score))
        
        scored_cards.sort(key=lambda x: x[1])
        return scored_cards[0][0] if scored_cards else None
    
    def evaluate_position(self) -> float:
        """Оценка текущей позиции ИИ"""
        if not self.hand:
            return 1.0  # Выигрышная позиция
        
        score = 0.0
        
        # Учитываем количество и качество карт
        trump_cards = sum(1 for card in self.hand if card.suit == self.trump_suit)
        high_cards = sum(1 for card in self.hand 
                        if Card.RANKS.index(card.rank) >= Card.RANKS.index('Q'))
        
        # Нормализованный счет за карты
        cards_score = (trump_cards * 0.4 + high_cards * 0.3) / len(self.hand)
        
        # Учитываем соотношение количества карт
        cards_ratio = len(self.hand) / (self.opponent_cards_count + 1)
        ratio_score = 1.0 - min(cards_ratio, 1.0)  # Меньше карт - лучше
        
        # Учитываем оставшиеся карты в колоде
        deck_factor = 1.0 if self.deck_remaining == 0 else 0.7
        
        score = (cards_score * 0.4 + ratio_score * 0.4) * deck_factor
        
        return min(max(score, 0.0), 1.0)  # Нормализуем от 0 до 1 