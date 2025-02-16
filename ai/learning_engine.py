import json
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
from game.durak_game import Card
import os

class GameState:
    def __init__(self, hand: List[Card], table: List[Card], trump_suit: str,
                 opponent_cards: int, deck_remaining: int):
        self.hand = hand
        self.table = table
        self.trump_suit = trump_suit
        self.opponent_cards = opponent_cards
        self.deck_remaining = deck_remaining

class GameAction:
    def __init__(self, action_type: str, card: Card = None):
        self.type = action_type  # attack, defend, take, done, add
        self.card = card

class GameResult:
    def __init__(self, won: bool, moves_count: int):
        self.won = won
        self.moves_count = moves_count

class LearningEngine:
    def __init__(self, save_dir: str = "ai_data"):
        self.save_dir = save_dir
        self.game_history: List[Tuple[GameState, GameAction, float]] = []
        self.weights = self._load_weights()
        self.app_specific_strategies = self._load_app_strategies()
        self.current_app = None
        self.games_played = 0
        self.games_won = 0
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def _load_weights(self) -> Dict[str, float]:
        try:
            with open(f"{self.save_dir}/weights.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "rank_weight": 0.4,
                "trump_weight": 0.3,
                "same_rank_weight": 0.1,
                "opponent_cards_weight": 0.2,
                "deck_remaining_weight": 0.1,
                "aggressive_factor": 0.5
            }
    
    def _load_app_strategies(self) -> Dict[str, Dict]:
        try:
            with open(f"{self.save_dir}/app_strategies.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def detect_current_app(self, window_title: str):
        """Определение текущего приложения по заголовку окна"""
        self.current_app = window_title
        if window_title not in self.app_specific_strategies:
            self.app_specific_strategies[window_title] = {
                "preferred_moves": {},
                "success_rate": 0.0,
                "games_played": 0,
                "typical_patterns": []
            }
    
    def record_move(self, state: GameState, action: GameAction, result_score: float):
        """Запись хода для обучения"""
        self.game_history.append((state, action, result_score))
        
        # Обновляем статистику для конкретного приложения
        if self.current_app:
            key = f"{action.type}_{action.card if action.card else 'none'}"
            stats = self.app_specific_strategies[self.current_app]["preferred_moves"]
            if key not in stats:
                stats[key] = {"count": 0, "success": 0.0}
            stats[key]["count"] += 1
            stats[key]["success"] += result_score
    
    def learn_from_game(self, game_result: GameResult):
        """Обучение на основе результатов игры"""
        self.games_played += 1
        if game_result.won:
            self.games_won += 1
        
        # Обновляем веса на основе истории игры
        for state, action, score in self.game_history:
            self._update_weights(state, action, score, game_result)
        
        # Обновляем статистику приложения
        if self.current_app:
            app_stats = self.app_specific_strategies[self.current_app]
            app_stats["games_played"] += 1
            app_stats["success_rate"] = self.games_won / self.games_played
            
            # Анализируем паттерны игры
            self._analyze_patterns()
        
        # Сохраняем обновленные данные
        self._save_data()
        
        # Очищаем историю текущей игры
        self.game_history.clear()
    
    def _update_weights(self, state: GameState, action: GameAction, score: float, 
                       game_result: GameResult):
        """Обновление весов на основе результата хода"""
        learning_rate = 0.1
        
        # Корректируем веса на основе успешности хода
        success_factor = 1.0 if game_result.won else -0.5
        
        self.weights["rank_weight"] += learning_rate * score * success_factor
        self.weights["trump_weight"] += learning_rate * score * success_factor
        
        # Корректируем агрессивность на основе результата
        if game_result.won and game_result.moves_count < 20:
            self.weights["aggressive_factor"] += learning_rate
        elif not game_result.won:
            self.weights["aggressive_factor"] -= learning_rate
        
        # Нормализуем веса
        self._normalize_weights()
    
    def _analyze_patterns(self):
        """Анализ паттернов успешной игры"""
        if len(self.game_history) < 3:
            return
            
        patterns = []
        for i in range(len(self.game_history) - 2):
            pattern = self.game_history[i:i+3]
            if all(score > 0.7 for _, _, score in pattern):
                patterns.append([
                    (a.type, str(a.card) if a.card else "none")
                    for _, a, _ in pattern
                ])
        
        if patterns:
            self.app_specific_strategies[self.current_app]["typical_patterns"] = patterns
    
    def get_strategy_adjustments(self) -> Dict[str, float]:
        """Получение корректировок стратегии для текущего приложения"""
        if not self.current_app:
            return {}
            
        app_stats = self.app_specific_strategies[self.current_app]
        
        # Рассчитываем корректировки на основе статистики
        adjustments = {
            "rank_weight": 1.0,
            "trump_weight": 1.0,
            "aggressive_factor": 1.0
        }
        
        if app_stats["games_played"] > 0:
            # Корректируем на основе успешности
            success_rate = app_stats["success_rate"]
            if success_rate < 0.4:
                adjustments["aggressive_factor"] = 0.7  # Играем осторожнее
            elif success_rate > 0.6:
                adjustments["aggressive_factor"] = 1.3  # Играем агрессивнее
            
            # Анализируем предпочтительные ходы
            moves = app_stats["preferred_moves"]
            if moves:
                best_moves = sorted(
                    moves.items(),
                    key=lambda x: x[1]["success"] / x[1]["count"] if x[1]["count"] > 0 else 0,
                    reverse=True
                )
                
                # Корректируем веса на основе успешных ходов
                for move, stats in best_moves[:3]:
                    if "trump" in move and stats["success"] / stats["count"] > 0.7:
                        adjustments["trump_weight"] *= 1.2
                    if "high" in move and stats["success"] / stats["count"] > 0.7:
                        adjustments["rank_weight"] *= 1.2
        
        return adjustments
    
    def _normalize_weights(self):
        """Нормализация весов"""
        total = sum(w for w in self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
    
    def _save_data(self):
        """Сохранение данных обучения"""
        with open(f"{self.save_dir}/weights.json", "w") as f:
            json.dump(self.weights, f)
        
        with open(f"{self.save_dir}/app_strategies.json", "w") as f:
            json.dump(self.app_specific_strategies, f)
        
        # Сохраняем статистику
        stats = {
            "last_update": datetime.now().isoformat(),
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": self.games_won / self.games_played if self.games_played > 0 else 0
        }
        with open(f"{self.save_dir}/statistics.json", "w") as f:
            json.dump(stats, f)
    
    def get_statistics(self):
        """Получение текущей статистики"""
        return {
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": self.games_won / self.games_played if self.games_played > 0 else 0
        } 