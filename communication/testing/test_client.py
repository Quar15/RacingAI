import signal
import sys
import socket
from multiprocessing.connection import Listener, Client
from array import array

SERVER_ADDRESS = ('192.168.1.27', 6000)
CLIENT_ADDRESS = ('localhost', 6000)


def ctrl_c_hit(*args, **kwargs):
    print('CTRL-c hit!')
    sys.exit(0)


def initialize_layers(neurons_init):
    for layer in neurons_init:
        # init layers
        for n in range(len(layer)):
            # init single neurons
            continue

    # print(neurons_init)


def init_with_server():
    # Layers initialization
    with Client(SERVER_ADDRESS, authkey=b'client') as conn:
        # Receive number of layers
        n_layers = conn.recv()
        neurons_init = []
        for i in range(n_layers):
            neurons_init.append([])
            n_neurons_in_layer = conn.recv()
            for j in range(n_neurons_in_layer):
                # Receive one neuron weight and bias
                arr = array('f', [0, 0])
                conn.recv_bytes_into(arr)

                neurons_init[i].append(arr)

        n_data = array('i', [0, 0])
        conn.recv_bytes_into(n_data)
        
    initialize_layers(neurons_init)

    return n_data


def dump_neurons_to_server():
    with Listener(CLIENT_ADDRESS, authkey=b'server_dump') as listener:
        with listener.accept() as conn:
            print('Connection accepted from', listener.last_accepted)
            
            # @TODO: Change to dump every neuron to server
            ### dummy data
            neurons = [1]
            neuron_layer = 1
            ###

            conn.send(len(neurons)) # send number of neurons to receive

            for neuron in neurons:
                conn.send(neuron_layer) # send hidden layer index
                conn.send_bytes(array('f', [0.0, 2.5])) # send weight and bias


def receive_data_from_server():
    # Receive input for first layer
    with Client(SERVER_ADDRESS, authkey=b'client') as conn:
        n_inputs = conn.recv()
        arr = array('f', [0] * n_inputs)
        conn.recv_bytes_into(arr)
        print(arr)
    
    return arr


def send_data_to_server(output_data):
    
    with Listener(CLIENT_ADDRESS, authkey=b'server') as listener:
        with listener.accept() as conn:
            print('Connection accepted from', listener.last_accepted)

            conn.send_bytes(array('f', output_data))


def main():

    n_data = init_with_server()
    print(f"Number of data to receive: {n_data[0]}, Number of data to send: {n_data[1]}")

    print("@INFO: Waiting for server")

    signal.signal(signal.SIGINT, ctrl_c_hit)

    # Main loop - receive, handle, send back
    while True:
        try:
            # Send how many neurons will be needed
            with Listener(CLIENT_ADDRESS, authkey=b'server') as listener:
                with listener.accept() as conn:
                    print('Connection accepted from', listener.last_accepted)
                    conn.send_bytes(array('i', [n_data[0], n_data[1]])) # Number of data to receive, number of data to send back

            server_data = receive_data_from_server()

            # Send last layer output to Server
            output_data = [1] * n_data[1] # @TODO: Change to real last layer data [Preferrable new function]
            send_data_to_server(output_data)
        
        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError):
            print("Connection Lost")
            break


if __name__ == "__main__":
    main()