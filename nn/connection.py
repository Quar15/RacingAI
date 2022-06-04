import socket
from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np

UNITY_IP = "127.0.0.1"
UNITY_PORT = 5066

HEADER_SIZE = 16


def init_TCP(*, address=UNITY_IP, port=UNITY_PORT) -> socket.socket:
    address = (UNITY_IP, UNITY_PORT)
    # address = ('192.168.0.107', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    # # print(socket.gethostbyname(socket.gethostname()))
    s.connect(address)
    return s


def send_msg_to_unity(s, args):
    msg = "%.1f " * len(args) % args
    msg = "#" + msg + "#"
    while len(msg) % 16 != 0:
        msg += " "

    msg = f"{len(msg):<{HEADER_SIZE}}" + msg
    try:
        s.send(bytes(msg, "utf-8"))
    except TimeoutError:
        pass


def handle_data(socket, data: str, handler: Callable[[str], Any]):
    response = handler(data)

    send_msg_to_unity(socket, response)


def listen_for_unity(s, handler: Callable[[str], Any]):
    full_msg = ""
    new_msg = True
    while True:
        try:
            msg = s.recv(16)
        except TimeoutError:
            continue

        if msg == b"":
            continue

        if new_msg:
            try:
                msg_len = int(msg[:HEADER_SIZE])
                new_msg = False

            # Catch possible shutdown message
            except ValueError:
                if msg.decode("utf-8") == "stop":
                    return
                raise

        full_msg += msg.decode("utf-8")

        # print(msg_len, len(full_msg)-HEADER_SIZE)

        if len(full_msg) - HEADER_SIZE == msg_len:
            response = handler(full_msg)
            if response is not None:
                send_msg_to_unity(s, response)
            # handle_data(s, full_msg, handler)
            new_msg = True
            full_msg = ""


@dataclass(eq=True, order=True, frozen=True)
class Message:
    """Holds all the data received from Unity."""

    generation: int
    car_id: int
    sensor_data: np.ndarray
    car_position: np.ndarray
    car_speed: np.ndarray
    checkpoint_position: np.ndarray
    direction: float
    score: float

    @staticmethod
    def parse_message(data: str) -> Optional["Message"]:
        """Tries to parse raw data received from Unity connection. Returns `Message` on success, otherwise returns `None`"""
        try:
            data = data.split("#")[1]
            data = data.replace(",", ".")
            data = data.split(" ")

            if data == [""]:
                return None

            gen = int(data[0])
            car_id = int(data[1])
            sensor_data = np.array(data[2:9]).astype(float)
            car_pos = np.array(data[9:11]).astype(float)
            car_speed = float(data[11])
            checkpoint_position = np.array(data[12:14]).astype(float)
            dir_dot = float(data[14])
            score = float(data[15])

            return Message(
                gen,
                car_id,
                sensor_data,
                car_pos,
                car_speed,
                checkpoint_position,
                dir_dot,
                score,
            )
        except Exception:
            return None
