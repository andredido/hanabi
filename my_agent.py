import GameManager
from threading import Thread

gm = GameManager.GameManager('127.0.0.1', '1024', 1)
command = ''
while True:
    print('\nType ready when all the players are connected')
    command = input()
    if command == "ready":
        break
gm.ready()