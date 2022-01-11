import random

COLORS = ['red','yellow','green','white','blue']

class HanabiGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        if num_players < 4: self.hand_size = 5 
        else: self.hand_size = 4
            
    def set_state(self, hint_token, err_token, deck, table_cards, discarded_cards, players_cards, players, current_player):
        self.hint_token = hint_token
        self.err_token = err_token
        self.deck = deck
        self.table_cards = table_cards
        self.discarded_cards = discarded_cards
        self.players_card = players_cards
        self.points = sum(len(self.table_cards[k]) for k in COLORS) if err_token < 3 else 0
        self.players = players                                              #ordered list (order = players order)
        self.current_player = current_player

    def is_last_turn(self):
        return (len(self.deck)==0 and self.current_player == self.players[-1]) or (self.err_token == 3) or (self.points==25)
