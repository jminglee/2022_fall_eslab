import tank_battle_beta
import server
import threading

HOST = '192.168.43.68' # IP address
PORT = 8080 # Port to listen on (use ports > 1023)
operations = ["idle", "left", "right", "up", "down", "shot"]
events = [threading.Event() for i in range(len(operations))]

game = threading.Thread(target = tank_battle_beta.game, args=(events,))
game.start()

control = threading.Thread(target = server.server, args=(HOST, PORT, operations, events,))
control.start()

'''
while True:
    import random,time
    data = random.randint(1,5)
    for i in range(len(operations)):
        if i == int(data): events[i].set() 
        else:              events[i].clear()
    time.sleep(0.1)
'''