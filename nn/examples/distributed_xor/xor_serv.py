import sys
import argparse

import numpy as np

from nn.distributed import ServerManager
from nn.layers import Dense, Tanh

# MAX_CLIENTS = 2
# SERVER_ADDRESS = ("localhost", 6000)

# EPOCHS = 2000
# LEARNING_RATE = 0.03

XOR_INPUTS = np.reshape(
    [
        [0, 0],
        [0.06, 1.09],
        [1, 0],
        [0.80, 1.09],
        [0.14, 0.02],
        [0, 1],
        [1.18, 0.17],
        [1, 1],
    ],
    (8, 2, 1),
)
XOR_OUTPUTS = np.reshape([[0], [1], [1], [0], [0], [1], [1], [0]], (8, 1, 1))
NETWORK_STRUCTURE = [Dense(2, 3), Tanh(), Dense(3, 1), Tanh()]


def ctrl_c_hit(*args, **kwargs):
    print("@INFO: CTRL+C hit")
    sys.exit(0)


def user_tests(manager: ServerManager):
    while True:
        i1 = float(input("First input [0.0 - 1.0]\n"))
        i2 = float(input("Second input [0.0 - 1.0]\n"))

        output = manager.forward(np.reshape([i1, i2], (2, 1)))[0][0]

        print(f"Result: {round(output)} ({output})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distributed machine learning. Server side."
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="specify alternate port (default: 6000)",
        default=6000,
    )

    parser.add_argument(
        "-k",
        "--authkey",
        type=str,
        help="specify authorization key (default: ' ')",
        default=" ",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-w", "--workers", type=int, help="specify required worker count"
    )
    group.add_argument("-l", "--layers", type=int, help="specify layers per worker")

    parser.add_argument(
        "-r",
        "--learning-rate",
        type=float,
        help="specify learning rate (default: 0.05)",
        default=0.05,
    )
    parser.add_argument(
        "-e",
        "--epochs",
        type=int,
        help="specify epochs count (default: 2000)",
        default=2000,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    manager = ServerManager(
        NETWORK_STRUCTURE,
        ("127.0.0.1", args.port),
        bytes(args.authkey, "utf8"),
        client_count=args.workers,
        layers_per_client=args.layers,
    )
    input("Press Enter to continue...")

    manager.teach(XOR_INPUTS, XOR_OUTPUTS, args.epochs, args.learning_rate)

    input("End of learning. Press Enter to continue...")
    user_tests(manager)


if __name__ == "__main__":
    main()
