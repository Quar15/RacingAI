from dataclasses import dataclass
from enum import IntEnum, auto
from math import ceil
from multiprocessing.connection import Client, Connection, Listener
import sys
from typing import Any, TypeVar

import jsonpickle
from nn.layers.base import BaseLayer

from nn.losses import mse


T = TypeVar("T")


def chunk(seq: list[T], size: int) -> list[list[T]]:
    return list(seq[pos : pos + size] for pos in range(0, len(seq), size))


class MsgType(IntEnum):
    INIT = auto()
    FORWARD_REQUEST = auto()
    FORWARD_RESPONSE = auto()
    BACKWARD_REQUEST = auto()
    BACKWARD_RESPONSE = auto()
    DUMP_REQUEST = auto()
    DUMP_RESPONSE = auto()
    SHUTDOWN = auto()


@dataclass(eq=True, frozen=True)
class Message:
    type: MsgType
    data: Any = None


class ServerManager:
    def __init__(
        self,
        network: list[BaseLayer],
        address,
        authkey: bytes | None,
        *,
        client_count: int = None,
        layers_per_client: int = None,
    ):
        if client_count is None and layers_per_client is None:
            raise TypeError(
                "Missing argument: either 'client_count' or 'layers_per_client' is required"
            )

        if client_count is not None:
            layers_per_client = ceil(len(network) / client_count)
        else:
            client_count = ceil(len(network) / layers_per_client)

        self.network = network
        self.chunks = chunk(self.network, layers_per_client)

        self.listener = Listener(address, authkey=authkey)
        self.clients: list[Connection] = list()
        self.inputs = list()

        self.error = 0.0

        print(f"@INFO: Accepting connections on port {self.listener.address[1]}")
        for _ in range(client_count):
            conn = self.listener.accept()

            print("@INFO: Connection accepted from", self.listener.last_accepted)

            msg = Message(MsgType.INIT, self.chunks[len(self.clients)])

            conn.send(msg)  # Send client layers
            self.clients.append(conn)
            self.inputs.append(None)

        print("@INFO: All clients served for initialization")

    def __del__(self):
        msg = Message(MsgType.SHUTDOWN)
        for c in self.clients:
            c.send(msg)
            c.close()

        self.listener.close()

    def send_data_to_client(self, index, message):
        self.clients[index].send(message)

    def receive_data_from_client(self, index):
        return self.clients[index].recv()

    def forward(self, inputs):
        data = inputs
        for i in range(len(self.clients)):
            self.inputs[i] = data

            msg = Message(MsgType.FORWARD_REQUEST, data)
            self.clients[i].send(msg)

            data = self.clients[i].recv().data

        return data

    def backward(self, expected, got, learning_rate):
        self.error = 0.0

        loss = mse(expected, got)
        self.error += loss.error

        gradient = loss.gradient
        for i in reversed(range(len(self.clients))):
            msg = Message(MsgType.BACKWARD_REQUEST, (gradient, learning_rate))
            self.clients[i].send(msg)

            gradient = self.clients[i].recv().data

    def teach(self, inputs, outputs, epochs, learning_rate):
        for e in range(epochs):
            for x, y in zip(inputs, outputs):
                output = self.forward(x)

                self.backward(y, output, learning_rate)

            print(f"@INFO: Step {e+1}/{epochs}, Error = {self.error/len(inputs)}")

    def request_dump(self):
        dumped_layers = list()

        msg = Message(MsgType.DUMP_REQUEST)
        for c in self.clients:
            c.send(msg)

            resp: Message = c.recv()
            assert resp.type == MsgType.DUMP_RESPONSE

            dumped_layers.extend(resp.data)

        self.network = dumped_layers


class Worker:
    def __init__(self, address, authkey):
        try:
            conn = Client(address, authkey=authkey)
        except ConnectionRefusedError:
            print("Connection refused")
            sys.exit(1)
        self.conn = conn

        msg: Message = self.conn.recv()

        self.layers = msg.data

    def dump_neurons_to_server(self):
        msg = Message(MsgType.DUMP_RESPONSE, jsonpickle.encode(self.layers))

        self.conn.send(msg)

    def handle_data_from_server(self):
        try:
            msg: Message = self.conn.recv()
        except EOFError:
            print("@ERROR: Connection with server lost")
            sys.exit(1)

        match msg.type:
            case MsgType.DUMP_REQUEST:
                self.dump_neurons_to_server()
            case MsgType.FORWARD_REQUEST:
                self.forward(msg.data)
            case MsgType.BACKWARD_REQUEST:
                self.backward(msg.data)
            case MsgType.SHUTDOWN:
                self.shutdown()

    def forward(self, inputs):
        output = inputs
        for layer in self.layers:
            output = layer.forward(output)

        msg = Message(MsgType.FORWARD_RESPONSE, output)
        self.conn.send(msg)

    def backward(self, err):
        error, learning_rate = err

        for layer in reversed(self.layers):
            error = layer.backward(error, learning_rate)

        msg = Message(MsgType.BACKWARD_RESPONSE, error)
        self.conn.send(msg)

    def shutdown(self):
        print("@INFO: Shutdown request")
        sys.exit(0)
