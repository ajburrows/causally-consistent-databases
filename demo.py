from server import Server
from client import Client
import threading
import time
import clear_databases

clear_databases.main()
s1 = Server(65432, [65433], "server1")
s2 = Server(65433, [65432], "server2")
peer1 = Client(50001, 65432)

threading.Thread(target=s1.start_server).start()
threading.Thread(target=s2.start_server).start()
threading.Thread(target=peer1.start_server).start()
time.sleep(1)
print('\n')
peer1.registerWithServer()
peer1.writeToDataCenter("x,I lost my wedding ring")
time.sleep(1)

peer1.writeToDataCenter("y,I found it")


time.sleep(3)
print("simulation complete")
