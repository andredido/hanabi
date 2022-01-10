import GameManager
import random

def secure_play(state):
    return None

gm = GameManager.GameManager('127.0.0.1', '1024', 0)
command = ''
while True:
    print('\nType ready when all the players are connected')
    command = input()
    if command == "ready":
        break
gm.ready()
while(gm.check_running()):
    if( not gm.check_running()): break
    turn, data = gm.my_turn()
    if (turn):
        #my turn --> do some action
        if(int(gm.state.usedNoteTokens)==0 ):
            action = random.choice(['hint', 'play'])
        elif(int(gm.state.usedNoteTokens)==8):
            action = random.choice(['play', 'discard'])
        else:
            action = random.choice(['hint', 'play', 'discard'])

        if action == 'play':
            #play a card
            value = random.choice([0,1,2,3,4])
            if(gm.play_card(value)):
                print('Played')
        if action == 'hint':
            dest = random.choice(gm.get_players())
            type_hint = random.choice(['color','value'])
            if type_hint == 'color':
                value = random.choice(['red', 'blue', 'yellow', 'white', 'green'])
            else:
                value = random.choice([1,2,3,4,5])
            if(gm.give_hint(dest, type_hint, value)):
                print(f'Hint to {dest}')
        if action == 'discard':
            value = random.choice([0,1,2,3,4])
            if(gm.discard_card(value)):
                print(f'Discarded')
    gm.wait_for_turn()


del(gm)