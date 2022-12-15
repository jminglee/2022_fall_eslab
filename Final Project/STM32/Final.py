import socket
import matplotlib.pyplot as plt

HOST = '192.168.0.115' # IP address
PORT = 8080 # Port to listen on (use ports > 1023)
operations = ["idle", "left", "right", "up", "down", "shot"]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Starting server at: ", (HOST, PORT))
    conn, addr = s.accept()
    with conn:
        print("Connected at", addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            print(f"Received from socket server: {operations[int(data)]}")
            if data == '': break
