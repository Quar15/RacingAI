import socket
import sys

import numpy as np

from nn.genetic import NetworkPool, BestPicker
from nn.layers import Dense, Tanh

# np.set_printoptions(15)
UNITY_IP = "127.0.0.1"
UNITY_PORT = 5066

HEADER_SIZE = 16

MUTATION_RATE = 0.5
PERTURBING_RATE = 0.9
POPULATION_COUNT = 10

CHECKPOINT_INTERVAL = 10

# usage: python UnityConnection.py [<save_dir>] [<load_saved_from>]
if len(sys.argv) > 2:
    pool = NetworkPool.from_file(sys.argv[2], 50, BestPicker())
    print(f"Loaded from {sys.argv[2]}")
else:
    pool = NetworkPool(
        POPULATION_COUNT,
        BestPicker(),
        [
            Dense(6, 12),
            Tanh(),
            Dense(12, 2),
            Tanh(),
        ],
    )
fitnesses = [-1000.0] * POPULATION_COUNT
prev_gen = 0
first = True


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


def handle_unity_data(data):

    data = data.split("#")[1]
    data = data.replace(",", ".")
    data = data.split(" ")

    if data == [""]:
        return
    # print(data)

    gen = int(data[0])
    car_id = int(data[1])
    sensor_data = np.array(data[2:9]).astype(float)
    # car_pos = np.array(data[9:11]).astype(float)
    car_speed = float(data[11])
    # checkpoint_position = np.array(data[12:14]).astype(float)
    # dir_dot = float(data[14])
    score = float(data[15])

    global prev_gen
    global first
    if gen > prev_gen and not first:
        # print(f"{fitnesses=}")
        pool.next_generation(MUTATION_RATE, PERTURBING_RATE, fitnesses, 1)
        print(f"Gen {prev_gen} stats:\nBest score: {pool.best_score}")

        if pool.generation % CHECKPOINT_INTERVAL == 0 and len(sys.argv) > 1:
            pool.to_file(f"gen{pool.generation}", sys.argv[1])
            print(f"Saved to {sys.argv[1]}/gen{pool.generation}")

        prev_gen += 1
        first = False

    vert, hor = pool.forward(
        car_id,
        [
            sensor_data[0],
            sensor_data[2],
            sensor_data[3],
            sensor_data[4],
            sensor_data[6],
            car_speed,
        ],
    )

    # dummy_data = (0, 1, -1.0, 0.0) # generation, carID, verticalInput, horizontalInput
    # dummy_data = (gen, car_id, random.randint(-1,1), random.randint(-1,1))

    # print(f"{car_id=} = {score}")
    fitnesses[car_id] = score

    formatted_data = (gen, car_id, vert, hor)

    send_msg_to_unity(tcp_socket, (formatted_data))


def listen_for_unity(s):
    full_msg = ""
    new_msg = True
    while True:
        msg = s.recv(16)

        if msg == b"":
            continue

        if new_msg:
            msg_len = int(msg[:HEADER_SIZE])
            new_msg = False

        full_msg += msg.decode("utf-8")

        # print(msg_len, len(full_msg)-HEADER_SIZE)

        if len(full_msg) - HEADER_SIZE == msg_len:
            handle_unity_data(full_msg)
            new_msg = True
            full_msg = ""


tcp_socket = init_TCP()


def main():
    listen_for_unity(tcp_socket)


if __name__ == "__main__":
    main()
