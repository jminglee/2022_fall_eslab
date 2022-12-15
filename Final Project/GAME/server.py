import socket
import threading

def server(HOST, PORT, operations, events):
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
                for i in range(operations):
                    if i == int(data): events[i].set() 
                    else:              events[i].clear()
                if data == '': break
