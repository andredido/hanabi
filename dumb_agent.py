#!/usr/bin/env python3
import GameManager
from threading import Thread
import os
from sys import argv, stdout
import random

if(len(argv)< 2):
    print('Provide an id number')

id = int(argv[1])

gm = GameManager.GameManager('127.0.0.1', '1024', id)

gm.ready()
#initial state err_token = 0 , hint_token = 0
turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards, hintRecieved = gm.get_state()
while(gm.check_running()):
    gm.wait_for_turn()
    turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards, hintRecieved = gm.get_state()
    myhintState = hintState[playerName]
    if (turn):
        #my turn --> do some action
        if(int(hint_token)==0 ):
            action = random.choice(['hint', 'play'])
        elif(int(err_token)==8):
            action = random.choice(['play', 'discard'])
        else:
            action = random.choice(['hint', 'play', 'discard'])

        if action == 'play':
            #play a card
            value = random.choice([0,1,2,3,4])
            if(gm.play_card(value)):
                print('Played')
        if action == 'hint':
            dest = random.choice(other_players)
            type_hint = random.choice(['color','value'])
            if type_hint == 'color':
                value = random.choice(['red', 'blue', 'yellow', 'white', 'green'])
            else:
                value = random.choice([1,2,3,4,5])
            if(gm.give_hint(dest, type_hint, value)):
                print(f'Hint to {dest}')
        if action == 'discard':
            value = random.choice([0,1,2,3,4])
            if(gm.discard_card(value)):
                print(f'Discarded')


del(gm)
