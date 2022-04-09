from cgi import test
import socket
import sys

import numpy as np

# np.set_printoptions(15)
UNITY_IP = "127.0.0.1"
UNITY_PORT = 5066

HEADER_SIZE = 16


def init_TCP():
    address = (UNITY_IP, UNITY_PORT)
    # address = ('192.168.0.107', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # # print(socket.gethostbyname(socket.gethostname()))
    s.connect(address)
    return s


def send_msg_to_unity(s, args):
    msg = "%.1f " * len(args) % args
    msg = "#" + msg + "#"
    while len(msg) % 16 != 0:
        msg += " "

    msg = f"{len(msg):<{HEADER_SIZE}}" + msg
    s.send(bytes(msg, "utf-8"))


def handle_unity_data(data, action_index):

    data = data.split("#")[1]
    data = data.replace(",", ".")
    data = data.split(" ")

    if data == [""]:
        return

    gen = int(data[0])
    car_id = int(data[1])

    test_steering = [[1, 1], [1, 1], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [-1, -1], [-1, -1], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    test_steering += [[-1, 1], [-1, 1], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [1, -1], [1, -1], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    test_steering += [[1, -1], [1, -1], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [-1, 1], [-1, 1], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    test_steering += [[-1, -1], [-1, -1], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [1, 1], [1, 1], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    test_steering += [[0, 0]]
    vert, hor = test_steering[action_index % len(test_steering)]
    formatted_data = (gen, car_id, vert, hor)

    send_msg_to_unity(tcp_socket, (formatted_data))


def listen_for_unity(s):
    full_msg = ""
    new_msg = True
    action_index = 0
    while True:
        msg = s.recv(16)

        if msg == b"":
            continue

        if new_msg:
            msg_len = int(msg[:HEADER_SIZE])
            new_msg = False

        full_msg += msg.decode("utf-8")

        if len(full_msg) - HEADER_SIZE == msg_len:
            handle_unity_data(full_msg, action_index)
            new_msg = True
            full_msg = ""
            action_index += 1
            


tcp_socket = init_TCP()


def main():
    listen_for_unity(tcp_socket)


if __name__ == "__main__":
    main()
