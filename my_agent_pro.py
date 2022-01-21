#!/usr/bin/env python3

import GameManager
from threading import Thread
import os
from sys import argv, stdout
import random
import utils

if(len(argv)< 2):
    print('Provide an id number')

id = int(argv[1])
tn = 0
gm = GameManager.GameManager('127.0.0.1', '1024', id)

gm.ready()
#initial state err_token = 0 , hint_token = 0
turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards, hintRecieved,card_left = gm.get_state()
while(gm.check_running()):
    gm.wait_for_turn()
    turn, hint_token, err_token, playerName, other_players, hintState, table_cards, discarded_cards, players_card, num_cards, hintRecieved, card_left = gm.get_state()
    myhintState = hintState[playerName]
    if (turn):
        print('turn',tn)
        tn+=1
        print(f'\t{turn}, {hint_token}, {err_token}')
        print(f'\t{hintState}')
        print('\tPLAYERS CARDS')
        ok = True
        for player in other_players:
            print(f'\t{player}')
            for i, card in enumerate(players_card[player]):
                c,v = hintState[player][i]
                if c != 'unknown' and c !=card.color:
                    ok=False
                if v!=0 and v!= card.value:
                    ok = False
                print(f'\t\t({card.color},{card.value})')
        print('\tTABLE')
        for color in table_cards:
            print(f'\t\t{color} {len(table_cards[color])}')
        if not ok:
            print('PROBLEM!!!!!!!!!!!')
            break
        sp, ip = utils.play_best_card(other_players, myhintState, table_cards, players_card, discarded_cards, hintRecieved)
        if card_left == 0 and err_token <2:
            gm.play_card(ip)
            print(f'Played last card {ip}')
            break
        if(sp==1):
            gm.play_card(ip)
            print(f'Played sure card {ip}')
            continue
        if sp>0.75 and err_token<2:
            gm.play_card(ip)
            print(f'Played card {ip}')
            continue
        
        if(hint_token<8):
            b, t, d, v = utils.hint_playable_fast(other_players, players_card, hintState, table_cards)
            if b:
                gm.give_hint(d, t, v)
                print(f'Hinted player {d}, type {t}, value {v}')
                continue
        if(hint_token<8 and hint_token>4):
            b, t, d, v = utils.hint_useless_card(other_players, players_card, hintState, table_cards, discarded_cards)
            if b:
                gm.give_hint(d, t, v)
                print(f'Hinted player {d}, type {t}, value {v}')
                continue
            
        if(hint_token>0):#I can discard
            s, i = utils.sure_discard(myhintState, table_cards, discarded_cards)
            if s:
                gm.discard_card(i)
                print(f'Discarded card {i}')
                continue
            s, i = utils.discard_best_card(other_players, myhintState, table_cards, players_card, discarded_cards)
            if s>0:
                gm.discard_card(i)
                print(f'Discarded card {i}')
                continue
            else:
                gm.discard_card(0)
                print(f'Discarded card 0')
                continue                
        if(hint_token<8):    
            b, t, d, v = utils.hint_random(other_players, players_card, hintState, table_cards)
            if b:
                gm.give_hint(d, t, v)
                print(f'Hinted (randomly) player {d}, type {t}, value {v}')
                continue
        
        print('NOTHING DONE -- ATTENTION')
        break

del(gm)
