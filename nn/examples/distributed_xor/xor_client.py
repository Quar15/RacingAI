import argparse
import signal
import sys

from nn.distributed import Worker

SERVER_ADDRESS = ("localhost", 6000)


def ctrl_c_hit(*args, **kwargs):
    print("CTRL-c hit!")
    sys.exit(0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distributed machine learning. Client side."
    )

    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="specify server address (default: '127.0.0.1')",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="specify server port (default: 6000)",
        default=6000,
    )

    parser.add_argument(
        "-k",
        "--authkey",
        type=str,
        help="specify authorization key (default: ' ')",
        default=" ",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    conn = Worker((args.address, args.port), bytes(args.authkey, "utf8"))

    print("@INFO: Waiting for server")

    signal.signal(signal.SIGINT, ctrl_c_hit)

    while True:
        conn.handle_data_from_server()


if __name__ == "__main__":
    main()
