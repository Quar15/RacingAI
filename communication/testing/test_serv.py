import signal
import sys
import socket
from multiprocessing.connection import Listener, Client
from array import array

import random

CLIENTS_ADDRESSES = [('127.0.0.1', 6000), ("192.168.1.34", 6001)]
SERVER_ADDRESS = ('192.168.1.27', 6000)


def get_layers_array():
    # @TODO: Change dummy data to real neurons data
    layers = []
    for i in range(random.randint(5, 8)): # layers
        layers.append([])
        for j in range(random.randint(2, 5)): # neurons
            layers[i].append([random.randrange(0, 1), random.randrange(1, 5)]) # [weight, bias]

    return layers


def init_clients():
    print("@INFO: Listening on:", SERVER_ADDRESS)
    n_input = 2 # Number of input data from input layer
    for address in CLIENTS_ADDRESSES:
        with Listener(SERVER_ADDRESS, authkey=b'client') as listener:
            with listener.accept() as conn:
                print('Connection accepted from', listener.last_accepted)

                layers = get_layers_array()

                conn.send(len(layers)) # Send number of layers

                for i in range(len(layers)):
                    # Send number of neurons in layer
                    conn.send(len(layers[i]))

                    for n in layers[i]:
                        conn.send_bytes(array('f', n)) # Send neuron weight and bias

            
                conn.send_bytes(array('i', [n_input, len(layers[-1])])) # Send number of input that will be send to client and number of output that it should send back
                n_input = len(layers[-1])

                print('@INFO: Neurons sent to:', listener.last_accepted)

    print("@INFO: All clients served for initialization")


def send_data_to_client(client_address, data):
    with Listener(SERVER_ADDRESS, authkey=b'client') as listener:
        with listener.accept() as conn:
            print('Connection accepted from', listener.last_accepted)

            conn.send(len(data))
            conn.send_bytes(data)


def receive_data_from_client(client_address, n_data):
    with Client(client_address, authkey=b'server') as conn:
        arr = array('f', [0] * n_data)
        conn.recv_bytes_into(arr)

    return arr


def ctrl_c_hit(*args, **kwargs):
    print('@INFO: CTRL+C hit')
    sys.exit(0)


def main():

    print("@INFO: Waiting for Clients")

    init_clients()

    input("Press Enter to continue...")

    signal.signal(signal.SIGINT, ctrl_c_hit)

    client_data = array('f', [0] * 2) # @TODO: Change to real input data for first hidden layer

    for i in range(len(CLIENTS_ADDRESSES)):

        # Receive how many neurons will be needed
        with Client(CLIENTS_ADDRESSES[i], authkey=b'server') as conn:
            arr = array('i', [0, 0])
            conn.recv_bytes_into(arr)
        print(f"@INFO: Client{i} needs {arr[0]} inputs and will send {arr[1]} outputs")

        client_data = array('f', [0] * arr[0]) # @TODO: Remove this, dummy data

        send_data_to_client(CLIENTS_ADDRESSES[i], client_data)
        client_data = receive_data_from_client(CLIENTS_ADDRESSES[i], arr[1])

        print(f"\n@INFO: Received data ({client_data})\n")

    # @TODO: Handle client data

    input("Press Enter to end...")


if __name__ == "__main__":
    main()