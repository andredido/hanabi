#!/usr/bin/env python3
import GameManager
from threading import Thread
import os
from sys import argv, stdout
import random

if(len(argv)< 2):
    print('Provide an id number')

id = int(argv[1])

gm1 = GameManager.GameManager('127.0.0.1', '1024', id)
command = ''
while True:
    print('\nType ready when all the players are connected')
    command = input()
    if command == "ready":
        break
gm1.ready()
while(gm1.check_running()):
    turn, data = gm1.my_turn()
    if (turn):
        #my turn --> do some action
        if(int(data.usedNoteTokens)==0 ):
            action = random.choice(['hint', 'play'])
        elif(int(data.usedNoteTokens)==8):
            action = random.choice(['play', 'discard'])
        else:
            action = random.choice(['hint', 'play', 'discard'])

        if action == 'play':
            #play a card
            value = random.choice([0,1,2,3,4])
            if(gm1.play_card(value)):
                print('Played')
        if action == 'hint':
            dest = random.choice(gm1.get_other_players())
            type_hint = random.choice(['color','value'])
            if type_hint == 'color':
                value = random.choice(['red', 'blue', 'yellow', 'white', 'green'])
            else:
                value = random.choice([1,2,3,4,5])
            if(gm1.give_hint(dest, type_hint, value)):
                print(f'Hint to {dest}')
        if action == 'discard':
            value = random.choice([0,1,2,3,4])
            if(gm1.discard_card(value)):
                print(f'Discarded')
    gm1.wait_for_turn()


del(gm1)
