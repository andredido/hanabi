#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread, Lock, Condition
import GameData
import socket
from constants import *
import os

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
        self.lock = Lock()
        self.cv = Condition()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.connect((HOST, PORT))
        request = GameData.ClientPlayerAddData(self.playerName)
        self.s.send(request.serialize())
        data = self.s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)
        assert type(data) is GameData.ServerPlayerConnectionOk
        print("Connection accepted by the server. Welcome " + self.playerName)
        print("[" + self.playerName + " - " + self.status + "]: ", end="")
        #Thread(target=self.listener).start()
    
    def __del__(self):
        if self.s is not None:
            self.run=False
            os._exit(0)
    
    def ready(self):
        if self.status == self.statuses[0]:
            self.s.send(GameData.ClientPlayerStartRequest(self.playerName).serialize())
            data = self.s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerPlayerStartRequestAccepted:
                print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
                self.position = data.acceptedStartRequests - 1
                data = self.s.recv(DATASIZE)
                data = GameData.GameData.deserialize(data)
                if type(data) is GameData.ServerStartGameData:
                    self.players = data.players
                    self.status = self.statuses[1]
            
    
    def show_cards(self):
        self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())

    def play_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerPlayCardRequest(self.playerName, num_card).serialize())
        except:
            return False
        try:
            data = self.s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerPlayerMoveOk:
                return 1
            if type(data) is GameData.ServerPlayerThunderStrike:
                return -1
            
            return False
        except:
            return False
        
    def discard_card(self, num_card):
        try:
            self.s.send(GameData.ClientPlayerDiscardCardRequest(self.playerName, num_card).serialize())
        except:
            return False
        try:
            data = self.s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerActionValid:
                return True
            return False
        except:
            return False

    def give_hint(self,destination, type, value):
        assert type in ['color', 'value']
        try:
            self.s.send(GameData.ClientHintData(self.playerName, destination, type, value).serialize())
        except:
            return False
        try:
            data = self.s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerHintData:
                return True
            return False
        except:
            return False
    
    def get_players(self):
        return self.players

    def current_state(self):
        try: self.s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
        except ConnectionResetError: return
        while True:
            data = self.s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerGameStateData:
                self.state = data
                print(data)
                break
