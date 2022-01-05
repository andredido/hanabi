#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread, Lock, Condition
from time import thread_time
import GameData
import socket
from constants import *
import os
import game
import copy

class GameManager:
    def __init__(self, ip=HOST, port=PORT, ID=0):
        self.playerName = 'player'+str(ID+1)
        self.ip = ip
        self.port = port
        self.run = True
        self.statuses = ["Lobby", "Game", "GameHint"]
        self.status = self.statuses[0]
        self.hintState = ("", "")
        self.state = None
        self.players = []
        self.mycards = []
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
            self.receiver_th.join()
            self.run=False
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
                        self.players.remove(self.playerName)
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
                    print('Received:' , data)
                    if type(data) is GameData.ServerGameStateData:
                        data: GameData.ServerGameStateData
                        print('Setting state')
                        with self.cv_state:
                            self.state = data
                            self.cv_state.notify_all()

                    elif type(data) is GameData.ServerHintData:
                        data: GameData.ServerHintData
                        

                    elif type(data) is GameData.ServerPlayerMoveOk or type(data) is GameData.ServerPlayerThunderStrike:
                        data: GameData.ServerPlayerMoveOk
                        

                    elif type(data) is GameData.ServerActionValid:
                        data: GameData.ServerActionValid

                    elif type(data) is GameData.ServerGameOver:
                        self.run = False
                        raise StopIteration

        except ConnectionResetError:
            with self.lock:
                self.run = False
            with self.cv_state:
                self.cv_state.notify_all()

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

    def my_turn(self):
        data = self.current_state()
        return data.currentPlayer == self.playerName

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
