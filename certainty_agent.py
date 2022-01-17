#!/usr/bin/env python3

#Certainty Agent: While information has to be
#given on playable cards and useless cards, give the information. Play a card as
#soon as this card is playable with certainty. Discard a card as soon as this card
#is discardable with certainty. When blue tokens are missing, discard the oldest
#card of your hand.

import GameManager
from threading import Thread
import os
from sys import argv, stdout
import random
import utils

if(len(argv)< 2):
    print('Provide an id number')

id = int(argv[1])

gm = GameManager.GameManager('127.0.0.1', '1024', id)
command = ''
while True:
    print('\nType ready when all the players are connected')
    command = input()
    if command == "ready":
        break
gm.ready()
while(gm.check_running()):
    turn, data = gm.my_turn()
    players = gm.get_other_players()
    myhintState = gm.get_myhintState()
    table_cards = gm.get_table_cards()
    discarded_cards = gm.get_discarded_cards()
    players_card = gm.get_players_cards()
    hintState = gm.get_hintState()

    if (turn):
        idx_card = utils.play_safe_card(myhintState, table_cards)
        if idx_card != False:
            gm.play_card(idx_card)
            continue
        if(data.usedNoteTokens == 0):
            #give a hint
            type,dest, value =  utils.best_hint(players, players_card, hintState, table_cards)
            if type:
                print(f'Hint to {dest} - {type}, {value}')
                gm.give_hint(dest, type, value)
                continue
            else:
                type,dest, value =  utils.useless_hint(players, players_card, hintState, table_cards)
                print(f'Hint to {dest} - {type}, {value}')
                gm.give_hint(dest, type, value)
                
        idx_card = utils.discard_safe_card(myhintState, table_cards)
        if idx_card != False:
            gm.play_card(idx_card)
            continue
        if(int(data.usedNoteTokens)<8):
            #I can give a hint
            
            type,dest, value =  utils.best_hint(players, players_card, hintState, table_cards)
            if type:
                print(f'Hint to {dest} - {type}, {value}')
                gm.give_hint(dest, type, value)
                continue
        
        for i, (c,v) in reversed(list(enumerate(myhintState))):
            if not utils.check_unique_remained(c, v, discarded_cards):
                print('discard oldest card')
                gm.discard_card(i)
                break
    gm.wait_for_turn()


del(gm)
