#!/usr/bin/env python3
import numpy as np

def play_best_card(players, my_hand, table_cards, playersCard, discarded_cards):
    scores = []
    for i, (c, v) in enumerate(my_hand):
        #I know all informations about the card
        if c != 'unknown' and v != 0: 
            if len(table_cards[c]) == v-1:
                scores.append(1.0)
            else:
                scores.append(0.0)
        #I know only the color
        elif c != 'unknown': 
            if len(table_cards[c])>0:
                last_card_table = table_cards[c][-1].value
            else:
                last_card_table = 1
            remaining = 0
            total_cards = 10
            if last_card_table == 1: remaining = 3
            elif last_card_table == 5: remaining = 1
            else: remaining = 2

            for player in players:
                for card in playersCard[player]:
                    if card.value == last_card_table and card.color == c:
                        remaining -= 1
                    if card.color == c:
                        total_cards -=1
                        
            for card in discarded_cards:
                if card.value == last_card_table and card.color == c:
                    remaining -= 1
                if card.color == c:
                    total_cards -=1
            
            if total_cards == 0:
                scores.append(0.0)
            else:
                scores.append(remaining/total_cards)   #probability that this is the right card

        #I know only the value
        elif v != 0:
            if(v == 1):#fisrt card
                num_card_colors = []
                for color in table_cards:
                    num_card_colors.append(len(table_cards[color]))
                if all(j == 0 for j in num_card_colors):
                    scores.append(1.0)
                    continue
            remaining = 0
            playable_colors = []
            for color in table_cards:
                if len(table_cards[color]) == v-1:
                    playable_colors.append(color)
                    
            if v ==1: 
                remaining = len(playable_colors) * 3
                total_cards = 15
            elif v ==5: 
                remaining = len(playable_colors)
                total_cards = 5
            else : 
                remaining = len(playable_colors) * 2
                total_cards = 10
            
            for player in players:
                for card in playersCard[player]:
                    if card.value == v and card.color in playable_colors:
                        remaining -= 1
                    if card.value == v:
                        total_cards -= 1
            
            for card in discarded_cards:
                if card.value == v and card.color in playable_colors:
                    remaining -= 1
                if card.value == v:
                    total_cards -= 1
            if total_cards == 0:
                scores.append(0.0)
            else:
                scores.append(remaining/total_cards)
        else:
            scores.append(0.0)
            
    best_card = np.argmax(scores)

    return scores[best_card], best_card
    
def useless_color(color, table_cards, discarded_cards):
    if len(table_cards[color]) == 5: #color completed
        return True, 6
    for i in range(len(table_cards[color])+1, 6):#search in all of remaining cards
        remaining = 0
        if i == 1 :     remaining = 3
        elif i == 5:    remaining = 1
        else:           remaining = 2
        for card in discarded_cards:
            if card.value == i and card.color == color:
                remaining -= 1
        if remaining <=0: return True, i
    return False, -1
def sure_discard( my_hand, table_cards, discarded_cards):
    for i, (c, v) in enumerate(my_hand):
        if c !='unknown' and v != 0:
            if v < len(table_cards[c]) +1 or len(table_cards[c])==5:
                return True, i
            b, j = useless_color(c, table_cards, discarded_cards)
            if b and j<=v:
                return True, i
        elif c!='unknown':
            if len(table_cards[c])==5:
                return True, i
            b, j = useless_color(c, table_cards, discarded_cards)
            if b and j<=v:
                return True, i
        elif v!=0:
            v_min = []
            colors = []
            for color in table_cards:
                v_min.append(len(table_cards[color]))
                if v == len(table_cards[color]) +1:
                    colors.append(color)
            if all(v <= k for k in v_min):
                return True, i
    return False, -1

def discard_best_card(players, my_hand, table_cards, playersCard, discarded_cards):
    scores = []
    for c, v in my_hand:
        if v!= 0 and c!='unknown':
            b, i = useless_color(c, table_cards, discarded_cards)
            if len(table_cards[c]) == 5:
                scores.append(1.0)
            elif (v<len(table_cards[c])+1):
                scores.append(1.0)
            elif b and i<=v:
                scores.append(1.0)
            else:
                scores.append(0.0)
        elif c!='unknown':
            b, i = useless_color(c, table_cards, discarded_cards)
            if len(table_cards[c]) == 5:
                scores.append(1.0)
            elif b and i<=v:
                scores.append(1.0)
            else:
                total_cards = 10
                remaining  = 0
                for i in range(len(table_cards[c])+1, 6):
                    if i==1:
                        remaining +=3
                    elif i==5:
                        remaining +=1
                    else:
                        remaining +=2
                for player in players:
                    for card in playersCard[player]:
                        if card.value<= len(table_cards[c]) and card.color == c:
                            remaining -= 1
                        if card.color == c:
                            total_cards -= 1
                for card in discarded_cards:
                    if card.value<= len(table_cards[c]) and card.color == c:
                        remaining -= 1
                    if card.color == c:
                        total_cards -= 1
                if total_cards ==0: scores.append(1.0)
                else : scores.append(remaining/total_cards)
        elif v!= 0:
            v_min = []
            colors = []
            for color in table_cards:
                v_min.append(len(table_cards[color]))
                if v == len(table_cards[color]) +1:
                    colors.append(color)
            if all(v <= k for k in v_min):
                scores.append(1.0)
            else:
                total_cards = 0
                remaining = 0
                if v == 5:  
                    total_cards = 5
                    remaining = len(colors)
                elif v ==1: 
                    total_cards = 15
                    remaining = 3 * len(colors)
                else:       
                    total_cards = 10
                    remaining = 2 * len(colors)

                for player in players:
                    for card in playersCard[player]:
                        if card.value == v and card.color in colors:
                            remaining -= 1
                        if card.value == v:
                            total_cards -= 1

                for card in discarded_cards:
                    if card.value == v and card.color in colors:
                        remaining -= 1
                    if card.value == v:
                        total_cards -= 1
                if total_cards ==0: scores.append(1.0)
                else : scores.append(remaining/total_cards)        
        else:
            scores.append(0.0)
    best_card = np.argmax(scores)

    return scores[best_card], best_card


def check_unique_remained(card_color, card_value, discarded_cards):
    if card_value == 5:
        return True
    remaining = 0
    if card_value == 1:
        remaining = 2
    else:
        remaining = 1
    for card in discarded_cards:
        if card.value == card_value and card.color == card_color:
            remaining -= 1
    if remaining<1:
        return True 
    return False
        

def hint_playable(players, playersCard, hintState, table_card):
    #hint next playable card
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if len(table_card[card.color]) == card.value-1:
                if v == 0:
                    return True, 'value', player, card.value
                elif c == 'unknown':
                    return True, 'color', player, card.color
    return False, '', '', 0

def hint_useless_card(players, playersCard, hintState, table_card, discarded_cards):
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if card.value < len(table_card[card.color]) +1 and v==0 :
                return True,'value', player, card.value
            elif len(table_card[card.color]) == 5 and c=='unknown':
                return True, 'color', player, card.color
            b, i = useless_color(card.color, table_card, discarded_cards) 
            if c == 'unknown' and b and i<card.value:
                return True, 'color', player, card.color
    return False, '', '', 0

def hint5(players, playersCard, hintState, table_card):
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if card.value == 5 and v == 0:
                return True, 'value', player, card.value
    return False, '', '', 0

def hint_random(players, playersCard, hintState, table_card):
    for player in players:
        for idx, card in enumerate(playersCard[player]):
            c, v = hintState[player][idx]
            if v == 0:
                return True, 'value', player, card.value
            if c == 'unknown':
                return True, 'color', player, card.color
    return False, '', '', 0

