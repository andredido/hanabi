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

gm.ready()
turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards = gm.get_state()
while(gm.check_running()):
    gm.wait_for_turn()
    turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards = gm.get_state()
    myhintState = hintState[playerName]
    if (turn):
        s, i = utils.play_best_card(other_players, myhintState, table_cards, players_card, discarded_cards)
        if(s==1):
            gm.play_card(i)
            print(f'Played card {i}')
            continue
        if(hint_token>0):#I can discard
            s, i = utils.discard_best_card(other_players, myhintState, table_cards, players_card, discarded_cards)
            if s == 1:
                gm.discard_card(i)
                print(f'Discarded card {i}')
                continue
        if(hint_token<8):
            b, t, d, v = utils.hint_playable(other_players, players_card, hintState, table_cards)
            if b:
                gm.give_hint(d, t, v)
                print(f'Hinted player {d}, type {t}, value {v}')
                continue
            b, t, d, v = utils.hint5(other_players, players_card, hintState, table_cards)
            if b:
                gm.give_hint(d, t, v)
                print(f'Hinted player {d}, type {t}, value {v}')
                continue

        if(hint_token>0):
            s, i = utils.discard_best_card(other_players, myhintState, table_cards, players_card, discarded_cards)
            gm.discard_card(i)
            print(f'Discarded card {i}')
            continue
        b, t, d, v = utils.hint_random(other_players, players_card, hintState, table_cards)
        if b:
            gm.give_hint(d, t, v)
            print(f'Hinted (useless) player {d}, type {t}, value {v}')
            continue
        print('NOTHING DONE -- ATTENTION')

del(gm)
