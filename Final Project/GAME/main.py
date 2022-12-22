import tank_battle
import tank_battle_pvp
import server
import threading

PLAYER = 2

if PLAYER == 1:
    HOST = '192.168.43.68'
    PORT = 8080
    operations = ["idle", "left", "right", "up", "down", "shot"]
    events = [threading.Event() for i in range(len(operations))]

    game = threading.Thread(target = tank_battle.game, args=(events,))
    game.start()

    control = threading.Thread(target = server.server, args=(HOST, PORT, operations, events,))
    control.start()

elif PLAYER == 2:
    HOST = '192.168.43.68'
    PORT1 = 8080
    PORT2 = 8080
    operations = ["idle", "left", "right", "up", "down", "shot"]
    events1 = [threading.Event() for i in range(len(operations))]
    events2 = [threading.Event() for i in range(len(operations))]

    game = threading.Thread(target = tank_battle_pvp.game, args=(events1,events2))
    game.start()

    control1 = threading.Thread(target = server.server, args=(HOST, PORT1, operations, events1,))
    control1.start()
    control2 = threading.Thread(target = server.server, args=(HOST, PORT2, operations, events2,))
    control2.start()

