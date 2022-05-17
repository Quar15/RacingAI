import argparse
from dataclasses import dataclass
from enum import Enum, auto
from socket import socket
from typing import Any

from connection import Message, init_TCP, listen_for_unity
from nn.genetic import BestPicker, NetworkPool
from nn.layers import Dense, Tanh
from nn.network import NeuralNetwork

MUTATION_RATE = 0.5
INTENSE_CROSS_RATE = 0.1
PERTURBING_RATE = 0.9
POPULATION_COUNT = 10

CHECKPOINT_INTERVAL = 10


def parse_args() -> argparse.Namespace:
    import os

    def is_dir(path: str) -> str:
        if os.path.isdir(path) or not os.path.exists(path):
            return path
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid path")

    parser = argparse.ArgumentParser(description="Unity Remote Car Controller")
    parser.add_argument(
        "-m",
        "--mode",
        help="select default mode",
        choices=["learning", "presentation"],
        default="learning",
    )
    parser.add_argument(
        "-i",
        "--save-interval",
        metavar="N",
        help="select checkpoint interval. ignored if mode is set to 'presentation' (Default: 10)",
        type=int,
        default=10,
    )
    parser.add_argument(
        "-s",
        "--save",
        metavar="PATH",
        help="select save directory (default: './saves')",
        type=is_dir,
        default="./saves",
    )
    parser.add_argument(
        "-l",
        "--load",
        metavar="PATH",
        help="load previously saved network",
        type=str,
    )

    return parser.parse_args()


class Mode(Enum):
    """All possible modes the `Manager` can be in."""

    INIT = auto()
    LEARNING = "learning"
    PRESENTATION = "presentation"
    # PAUSED = auto()


@dataclass()
class Manager:
    """The main `Manager` which controls argument parsing, neural network initializaion,
    connection initialization, data handling and mode switching."""

    pool: NetworkPool
    socket: socket
    fitness: list[float]
    save_interval: int
    save_directory: str
    mode: Mode = Mode.INIT
    current_gen: int = 0

    def __init__(self):
        args = parse_args()

        if args.load is not None:
            self.pool = NetworkPool.from_file(args.load, POPULATION_COUNT, BestPicker())
            self.fitness = self.pool.picker.fitnesses[:]

            while len(self.fitness) < POPULATION_COUNT:
                self.fitness.append(0.0)

        else:
            self.pool = NetworkPool(
                POPULATION_COUNT,
                BestPicker(),
                [
                    Dense(6, 12),
                    Tanh(),
                    Dense(12, 2),
                    Tanh(),
                ],
            )
            self.fitness = [-1000] * POPULATION_COUNT

        self.save_interval = args.save_interval
        self.save_directory = args.save

        self.socket = init_TCP()
        self.mode = Mode(args.mode)

    def set_mode(self, mode: Mode):
        """Switches manager to provided mode"""
        print(f"@INFO: Setting mode to {mode}")
        self.mode = mode

    def checkpoint(self) -> bool:
        """Creates a checkpoint"""
        self.pool.to_file(
            f"gen{self.pool.generation}",
            directory=self.save_directory,
            create_parents=True,
        )
        print(f"@INFO: Saved gen {self.pool.generation} at {self.save_directory}")

    def handle_learning(self, message: Message) -> Any:
        """Main handler for learning `Mode`"""
        if self.mode != Mode.LEARNING:
            print(f"@ERROR: Expected mode to be {Mode.LEARNING}, got {self.mode}")

        if message.generation > self.current_gen:
            if (
                self.save_interval > 0
                and self.pool.generation % self.save_interval == 0
            ):
                self.checkpoint()

            self.pool.next_generation(
                MUTATION_RATE, PERTURBING_RATE, INTENSE_CROSS_RATE, self.fitness, 2
            )
            self.current_gen += 1
            print(
                f"@INFO: Generation {self.pool.generation - 1} best score: {self.pool.best_score}"
            )

        return self.handle_presentation(message)

    def handle_presentation(self, message: Message, *, only_best: bool = False) -> Any:
        """Main handler for presentation `Mode`"""
        if self.mode != Mode.PRESENTATION and only_best:
            print(f"@ERROR: Expected mode to be {Mode.PRESENTATION}, got {self.mode}")

        inputs = [
            message.sensor_data[0],
            message.sensor_data[2],
            message.sensor_data[3],
            message.sensor_data[4],
            message.sensor_data[6],
            message.car_speed,
        ]

        if only_best:
            vert, hor = self.pool.best_network.forward(inputs)
        else:
            vert, hor = self.pool.forward(message.car_id, inputs)

        self.fitness[message.car_id] = message.score

        return (message.generation, message.car_id, vert, hor)

    def mode_switch(self, data: str) -> Any:
        """Main `Manager` handler, dispatching responses based on current `Mode`"""
        message = Message.parse_message(data)
        if message is None:
            return None

        match self.mode:
            case Mode.LEARNING:
                return self.handle_learning(message)
            case Mode.PRESENTATION:
                return self.handle_presentation(message, only_best=True)

    def start_manager(self):
        """Main manager loop"""
        try:
            listen_for_unity(self.socket, self.mode_switch)
        except KeyboardInterrupt:
            print("@INFO: Received Ctrl-C")

            print("@DEBUG:", self.mode, Mode.LEARNING, self.mode == Mode.LEARNING)
            if self.mode == Mode.LEARNING:
                self.checkpoint()

            print("@DEBUG: Shutting down")
            exit(0)


if __name__ == "__main__":
    manager = Manager()
    manager.start_manager()
