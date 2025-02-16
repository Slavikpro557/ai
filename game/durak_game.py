import random
from typing import List, Optional

class Card:
    SUITS = ['♠', '♣', '♥', '♦']
    RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def can_beat(self, other: 'Card', trump_suit: str) -> bool:
        if self.suit == other.suit:
            return self.RANKS.index(self.rank) > self.RANKS.index(other.rank)
        return self.suit == trump_suit

class DurakGame:
    def __init__(self):
        self.deck: List[Card] = []
        self.player_hand: List[Card] = []
        self.ai_hand: List[Card] = []
        self.trump_card: Optional[Card] = None
        self.trump_suit: Optional[str] = None
        self.is_game_active = False
        
    def start_new_game(self):
        self.is_game_active = True
        self._initialize_deck()
        self._deal_initial_cards()
    
    def stop_game(self):
        self.is_game_active = False
        self.deck.clear()
        self.player_hand.clear()
        self.ai_hand.clear()
        self.trump_card = None
        self.trump_suit = None
    
    def _initialize_deck(self):
        self.deck = [Card(suit, rank) 
                    for suit in Card.SUITS 
                    for rank in Card.RANKS]
        random.shuffle(self.deck)
        self.trump_card = self.deck[-1]
        self.trump_suit = self.trump_card.suit
    
    def _deal_initial_cards(self):
        for _ in range(6):
            if self.deck:
                self.player_hand.append(self.deck.pop())
            if self.deck:
                self.ai_hand.append(self.deck.pop())
    
    def is_valid_move(self, card: Card, target_card: Optional[Card] = None) -> bool:
        if not target_card:
            return True
        return card.can_beat(target_card, self.trump_suit)
    
    def get_game_state(self):
        return {
            'player_hand': self.player_hand,
            'ai_hand_count': len(self.ai_hand),
            'trump_card': self.trump_card,
            'deck_count': len(self.deck),
            'is_game_active': self.is_game_active
        } 