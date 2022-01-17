#!/usr/bin/env python3

from sys import setswitchinterval
from threading import Thread, Lock, Condition
from time import thread_time
import GameData
import socket
from constants import *
from game import Card
import os
import copy

class GameManager:
    def __init__(self, ip=HOST, port=PORT, ID=0):
        self.playerName = 'player'+str(ID+1)
        self.ip = ip
        self.port = port
        self.run = True
        self.statuses = ["Lobby", "Game", "GameHint"]
        self.status = self.statuses[0]

        self.state = None
        self.hintState = {}
        self.hint_token = None
        self.err_token = None
        self.deck = None
        self.table_cards = { "red": [], "yellow": [], "green": [], "blue": [], "white": [] }
        self.discarded_cards = []
        self.players_card = {}
        self.players = []
        self.other_players = []
        self.num_cards = 0
        self.lock = Lock()
        self.cv = Condition()
        self.cv_state = Condition()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.connect((HOST, PORT))
        request = GameData.ClientPlayerAddData(self.playerName)
        self.s.send(request.serialize())
        data = self.s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)
        assert type(data) is GameData.ServerPlayerConnectionOk
        print("Connection accepted by the server. Welcome " + self.playerName)
        print("[" + self.playerName + " - " + self.status + "]: ", end="")
    
    def __del__(self):
        if self.s is not None:
            with self.lock:
                self.run=False
            with self.cv_state:
                self.cv_state.notify_all()
            with self.cv:
                self.cv.notify_all()

        os._exit(0)
    
    def ready(self):
        if self.status == self.statuses[0]:
            try: self.s.send(GameData.ClientPlayerStartRequest(self.playerName).serialize())
            except ConnectionResetError: return
            try:
                data = self.s.recv(DATASIZE)
                data = GameData.GameData.deserialize(data)
                if type(data) is GameData.ServerPlayerStartRequestAccepted:
                    print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
                    data = self.s.recv(DATASIZE)
                    data = GameData.GameData.deserialize(data)
                    if type(data) is GameData.ServerStartGameData:
                        self.s.send(GameData.ClientPlayerReadyData(self.playerName).serialize())
                        self.players = data.players
                        idx = self.players.index(self.playerName)
                        self.players = self.players[idx:] + self.players[:idx]          #ordered by turn
                        if len(self.players) >3: self.num_cards = 4
                        else: self.num_cards = 5
                        for p in self.players:
                            self.hintState[p] = []
                            for i in range(0,self.num_cards, 1):
                                self.hintState[p].append(('unknown', 0))
                        print(self.players)
                        self.other_players = list(self.players)
                        self.other_players.remove(self.playerName)
                        self.status = self.statuses[1]
                        self.receiver_th = Thread(target=self.receiver)
                        self.receiver_th.start()
                        print('Game Started!')
            except: return False
    
    def receiver(self):
        print('Starting thread')
        try:
            while self.run:
                data = self.s.recv(DATASIZE)
                if not data: continue
                data = GameData.GameData.deserialize(data)
                with self.lock:
                    if type(data) is GameData.ServerGameStateData:
                        data: GameData.ServerGameStateData
                        with self.cv_state:
                            self.state = data
                            self.hint_token = data.usedNoteTokens
                            self.err_token = data.usedStormTokens
                            for p in data.players:
                                if p.name != self.playerName:
                                    self.players_card[p.name] = [Card(card.id, card.value, card.color) for card in p.hand]
                            for col in data.tableCards.keys():
                                self.table_cards[col] = [Card(card.id, card.value, card.color) for card in data.tableCards[col]]
                            self.discarded_cards = []
                            for card in data.discardPile:
                                self.discarded_cards.append(Card(card.id, card.value, card.color))
                            self.cv_state.notify_all()

                    elif type(data) is GameData.ServerHintData:
                        data: GameData.ServerHintData
                        for i in data.positions:
                            c, v = self.hintState[data.destination][i]
                            if(data.type == 'value'):
                                v = data.value
                            else:
                                c = data.value
                            self.hintState[data.destination][i] = (c,v)

                    elif type(data) is GameData.ServerPlayerMoveOk \
                      or type(data) is GameData.ServerPlayerThunderStrike:
                        data: GameData.ServerPlayerMoveOk
                        del self.hintState[data.lastPlayer][data.cardHandIndex]
                        self.hintState[data.lastPlayer].append(('unknown', 0))

                    elif type(data) is GameData.ServerActionValid:
                        data: GameData.ServerActionValid

                    elif type(data) is GameData.ServerGameOver:
                        self.run = False
                        with self.cv_state:
                            self.cv_state.notify_all()
                        with self.cv:
                            self.cv.notify_all()
                        break
                    
                    with self.cv:
                        self.cv.notify_all()
            os._exit(0)

        except ConnectionResetError:
            with self.lock:
                self.run = False
            with self.cv_state:
                self.cv_state.notify_all()
            with self.cv:
                self.cv.notify_all()

    def play_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerPlayCardRequest(self.playerName, num_card).serialize())
        except:
            return False
        
    def discard_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerDiscardCardRequest(self.playerName, num_card).serialize())
        except:
            return False

    def give_hint(self,destination, type, value):
        assert type in ['color', 'value']
        try:
            self.s.send(GameData.ClientHintData(self.playerName, destination, type, value).serialize())
        except:
            return False
    
    def get_players(self):
        return self.players

    def get_other_players(self):
        return self.other_players
    
    def get_hintState(self):
        with self.lock:
            hs = dict(self.hintState)
        return hs
    
    def get_myhintState(self):
        with self.lock:
            hs = list(self.hintState[self.playerName])
        return hs

    def get_hintState(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            hS = dict(self.hintState)
        return hS
    
    def get_deck_cards(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            deck = dict(self.deck)
        return deck

    def get_players_cards(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            pcs = dict(self.players_card)
        return pcs
    
    def get_discarded_cards(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            discard = list(self.discarded_cards)
        return discard
    
    def get_table_cards(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            table = dict(self.table_cards)
        return table
    
    def wait_for_turn(self):
        with self.cv:
            self.cv.wait()

    def my_turn(self):
        data = self.current_state()
        return data.currentPlayer == self.playerName, data

    def current_state(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            data = copy.deepcopy(self.state)
        return data
    
    def check_running(self):
        with self.lock:
            run = self.run
        return run
