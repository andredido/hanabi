from sys import argv, stdout
from threading import Thread, Lock, Condition
import GameData
import socket
from constants import *
from collections import deque

class IntelligenceAgent:
    def __init__(self, ip=HOST, port=PORT, nmyAgent=0):
        self.statuses = ["Lobby", "Game", "GameHint"]
        self.status = self.statuses[0]
        self.playerName = "myAgent"
        if nmyAgent > 0:
            self.playerName += str(nmyAgent)
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request = GameData.ClientPlayerAddData(self.playerName)
        self.s.connect((ip, port))
        self.s.send(request.serialize())
        data = self.s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerPlayerConnectionOk:
            print("Connection accepted by the server. Welcome " + self.playerName)
        stdout.flush()

        self.lock = Lock()
        self.cv = Condition()
        self.run = True
    
    def __del__(self):
        self.s.close()