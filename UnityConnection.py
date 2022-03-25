import socket
import time
import random

import numpy as np


UNITY_IP = "127.0.0.1"
UNITY_PORT = 5066

HEADER_SIZE = 16

def init_TCP():
    address = (UNITY_IP, UNITY_PORT)
    # address = ('192.168.0.107', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print(socket.gethostbyname(socket.gethostname()))
    s.connect(address)
    return s


def send_msg_to_unity(s, args):
    msg = '%.1f ' * len(args) % args
    msg = '#' + msg + '#'
    while len(msg) % 16 != 0:
        msg += ' '
    
    msg = f"{len(msg):<{HEADER_SIZE}}" + msg
    s.send(bytes(msg, "utf-8"))


def handle_unity_data(data):

    data = data.split('#')[1]
    data = data.replace(',', '.')
    data = data.split(' ')

    if(data == ['']):
        return

    print(len(data), data)

    gen = int(data[0])
    car_id = int(data[1])
    sensor_data = np.array(data[2:9]).astype(float)
    car_position = np.array(data[9:11]).astype(float)
    checkpoint_position = np.array(data[11:13]).astype(float)
    dir_dot = float(data[13])
    score = float(data[14])

    print("DATA:", car_id, sensor_data, car_position, checkpoint_position, dir_dot, score)

    # dummy_data = (0, 1, -1.0, 0.0) # generation, carID, verticalInput, horizontalInput
    dummy_data = (gen, car_id, random.randint(-1,1), random.randint(-1,1))
    send_msg_to_unity(tcp_socket, (dummy_data))


def listen_for_unity(s):
    full_msg = ""
    new_msg = True
    while True:
        msg = s.recv(16)

        if msg == b'':
            continue

        if new_msg:
            msg_len = int(msg[:HEADER_SIZE])
            new_msg = False

        full_msg += msg.decode("utf-8")

        print(msg_len, len(full_msg)-HEADER_SIZE)

        if len(full_msg)-HEADER_SIZE == msg_len:
            handle_unity_data(full_msg)
            new_msg = True
            full_msg = ""

        
tcp_socket = init_TCP()

def main():
    listen_for_unity(tcp_socket)


if __name__ == "__main__":
    main()