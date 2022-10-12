import socket
import matplotlib.pyplot as plt

HOST = '192.168.108.35' # IP address
PORT = 8080 # Port to listen on (use ports > 1023)
t, x, y, z, gx, gy, gz = list(), list(), list(), list(), list(), list(), list()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Starting server at: ", (HOST, PORT))
    conn, addr = s.accept()
    with conn:
        print("Connected at", addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            print(f"Received from socket server:{data}")
            if data == '': break

            data = data.split(' ')
            x. append(float(data[0]))
            y. append(float(data[1]))
            z. append(float(data[2]))
            gx.append(float(data[3]))
            gy.append(float(data[4]))
            gz.append(float(data[5]))
            t. append(float(data[6]))
            plt.pause(0.0001) 

fig = plt.figure(figsize = plt.figaspect(0.5))
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')            
ax1.plot(gx, gy, gz)
ax1.set_xlabel('x', fontsize=16, rotation=150)
ax1.set_ylabel('y', fontsize=16)
ax1.set_zlabel('z', fontsize=16)
ax1.set_title("Gyro", fontsize=20)
ax2.plot(x, y, z)
ax2.set_xlabel('x', fontsize=16, rotation=150)
ax2.set_ylabel('y', fontsize=16)
ax2.set_zlabel('z', fontsize=16)
ax2.set_title("Acce", fontsize=20)
plt.show()