import GameManager
from threading import Thread

gm1 = GameManager.GameManager('127.0.0.1', '1024', 0)
command = ''
while True:
    print('\nType ready when all the players are connected')
    command = input()
    if command == "ready":
        break
gm1.ready()
while gm1.status == gm1.statuses[1]:
    gm1.current_state()
