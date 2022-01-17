#!/usr/bin/env python3

def play_safe_card(my_hand, table_cards):
    for i, (myCc, MyCv) in enumerate(my_hand):
        for color in table_cards:
            if color != myCc: continue
            if len(table_cards[color]>0 and table_cards[color][-1].value == MyCv):
                #play this card
                return i
    return False

def discard_safe_card(my_hand, table_cards):
    for i, (myCc, MyCv) in enumerate(my_hand):
        for color in table_cards:
            if color != myCc: continue
            if table_cards[color][-1].value == 5:
                return i
            for card in table_cards[color]:
                if MyCv == card.value:
                    #discard this card
                    return i
    return False

def check_unique_remained(card_color, card_value, discard_pile):
    if card_value == 5:
        return True
    remaining = 0
    if card_value == 1:
        remaining = 2
    else:
        remaining = 1
    for card in discard_pile:
        if card.value == card_value and card.color == card_color:
            remaining -= 1
    if remaining<1:
        return True 
    return False
        

def best_hint(players, playersCard, hintState, table_card):
    #hint next playable card
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if len(table_card[card.color])>0 and table_card[card.color][-1].value == card.value-1:
                if v == 0:
                    return 'value', player, card.value
                elif c == 'unknown':
                    return 'color', player, card.color
    #hint for 5, so you don't discard it
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if card.value == 5 and v == 0:
                return 'value', player, card.value
    return None, None, None

def useless_hint(players, playersCard, hintState, table_card):
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if v == 0:
                return 'value', player, card.value