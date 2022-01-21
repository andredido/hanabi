#!/usr/bin/env python3

from sys import setswitchinterval
from threading import Thread, Lock, Condition, Semaphore
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
        self.myTurn = False
        self.hintReceived = -1
        self.table_cards = { "red": [], "yellow": [], "green": [], "blue": [], "white": [] }
        self.discarded_cards = []
        self.players_card = {}
        self.players = []
        self.other_players = []
        self.card_left = 50
        self.num_cards = 0
        self.lock = Lock()
        self.sem = Semaphore()
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
            self.sem.release()
    
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
                            self.card_left -= self.num_cards*len(self.players)
                            self.hintState[p] = []
                            for i in range(0,self.num_cards, 1):
                                self.hintState[p].append(('unknown', 0))
                        self.other_players = list(self.players)
                        self.other_players.remove(self.playerName)
                        self.status = self.statuses[1]
                        self.receiver_th = Thread(target=self.receiver)
                        print('Game Started!')
                        self.receiver_th.start()
                        with self.cv_state:
                             self.cv_state.notify_all()
            except: return False
    
    def receiver(self):
        print('Starting thread')
        try:
            with self.lock:
                run = self.run
            while run:
                with self.lock:
                    run = self.run
                data = self.s.recv(DATASIZE)
                if not data: continue
                data = GameData.GameData.deserialize(data)
                with self.lock:
                    if type(data) is GameData.ServerActionInvalid:
                        data: GameData.ServerActionInvalid
                        self.sem.release()

                    if type(data) is GameData.ServerGameStateData:
                        data: GameData.ServerGameStateData
                        with self.cv_state:
                            self.myTurn = (data.currentPlayer == self.playerName)
                            self.state = data
                            self.hint_token = data.usedNoteTokens
                            self.err_token = data.usedStormTokens
                            self.card_left = 50-self.num_cards
                            for p in data.players:
                                if p.name != self.playerName:
                                    self.players_card[p.name] = [Card(card.id, card.value, card.color) for card in p.hand]
                                    self.card_left -= len(self.players_card[p.name])
                            for col in data.tableCards.keys():
                                self.table_cards[col] = [Card(card.id, card.value, card.color) for card in data.tableCards[col]]
                                self.card_left -= len(self.table_cards[col])
                            self.discarded_cards = []
                            for card in data.discardPile:
                                self.discarded_cards.append(Card(card.id, card.value, card.color))
                                self.card_left -= 1
                            self.cv_state.notify_all()

                    elif type(data) is GameData.ServerHintData:
                        data: GameData.ServerHintData
                        with self.cv_state:
                            if self.card_left == 0 and data.source == self.playerName:
                                self.card_left = -1
                            if(data.destination == self.playerName):
                                self.hintReceived = data.positions[-1] #Youngest card hinted
                            for i in data.positions:
                                c, v = self.hintState[data.destination][i]
                                if(data.type == 'value'):
                                    v = data.value
                                else:
                                    c = data.value
                                self.hintState[data.destination][i] = (c,v)
                            self.cv_state.notify_all()
                        self.sem.release()

                    elif type(data) is GameData.ServerPlayerMoveOk \
                      or type(data) is GameData.ServerPlayerThunderStrike:
                        data: GameData.ServerPlayerMoveOk
                        with self.cv_state:
                            if self.card_left == 0 and data.lastPlayer == self.playerName:
                                self.card_left = -1
                            self.hintState[data.lastPlayer].pop(data.cardHandIndex)
                            self.hintState[data.lastPlayer].append(('unknown', 0))
                            self.cv_state.notify_all()
                        self.sem.release()

                    elif type(data) is GameData.ServerActionValid:
                        data: GameData.ServerActionValid
                        with self.cv_state:
                            if self.card_left == 0 and data.lastPlayer == self.playerName:
                                self.card_left = -1
                            self.hintState[data.lastPlayer].pop(data.cardHandIndex)
                            self.hintState[data.lastPlayer].append(('unknown', 0))
                            self.cv_state.notify_all()
                        self.sem.release()

                    elif type(data) is GameData.ServerGameOver:
                        self.run = False
                        with self.cv_state:
                            self.cv_state.notify_all()
                        self.sem.release()
                        break
                    
                
                with self.cv_state:
                     self.cv_state.notify_all()
            os._exit(0)

        except ConnectionResetError:
            with self.lock:
                self.run = False
            with self.cv_state:
                self.cv_state.notify_all()            
            self.sem.release()

    def play_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerPlayCardRequest(self.playerName, num_card).serialize())
            with self.lock:
                self.hintReceived = -1
        except:
            return False
        
    def discard_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerDiscardCardRequest(self.playerName, num_card).serialize())
            with self.lock:
                self.hintReceived = -1
        except:
            return False

    def give_hint(self,destination, type, value):
        assert type in ['color', 'value']
        try:
            self.s.send(GameData.ClientHintData(self.playerName, destination, type, value).serialize())
            with self.lock:
                self.hintReceived = -1
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
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            turn = self.myTurn
        if turn:
            return
        self.sem.acquire()

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
    
    def get_state(self):
        with self.cv_state:
            try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
            except ConnectionResetError: return  
            self.cv_state.wait()
        with self.lock:
            turn = self.myTurn
            hint_token = self.hint_token
            err_token = self.err_token
            other_players = list(self.other_players)
            hintState = dict(self.hintState)
            table = dict(self.table_cards)
            discarded_cards = list(self.discarded_cards)
            players_card = dict(self.players_card)
            num_cards = self.num_cards
            hintRecieved = self.hintReceived
            card_left = self.card_left
        return turn, hint_token, err_token, self.playerName, other_players, hintState, table, discarded_cards, players_card, num_cards, hintRecieved, card_left

    def check_running(self):
        with self.lock:
            run = self.run
        return run
