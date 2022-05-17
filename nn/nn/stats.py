from copy import deepcopy
from typing import Optional
import numpy as np

from nn.network import NeuralNetwork


class Stats:
    current_network: Optional[NeuralNetwork] = None

    def __init__(self, network: NeuralNetwork = None):
        self.current_network = network

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(targets={self.targets.__repr__()}, current_network={self.current_network.__repr__()})"

    def summary(self, new_network: NeuralNetwork) -> str:
        # ↗↘
        o1 = np.reshape([2.3, 4.0, 6.0, 8.0, 25.0, 3.0], (6, 1))

        output = "\nInput:\n"
        for i, inp in enumerate(o1):
            output += f"{i+1}: {inp[0]:.2f} "

        output += "\n"

        if self.current_network is None:
            for i, l in enumerate(new_network.layers):
                o1 = l.forward(o1)

                output += f"{l.__class__.__name__}\n"

                for i, n in enumerate(o1):
                    output += f"{i+1}: {n[0]:.2f} "

                output += "\n"

            self.current_network = new_network
            return output

        o2 = deepcopy(o1)
        for i, (pl, cl) in enumerate(
            zip(self.current_network.layers, new_network.layers)
        ):
            o1 = pl.forward(o1)
            o2 = cl.forward(o2)

            output += f"{cl.__class__.__name__}:\n"

            for i, (n1, n2) in enumerate(zip(o1, o2)):
                n1, n2 = n1[0], n2[0]
                output += f"{i+1}: {n1:.2f}({(n2-n1):.2f}) "

            output += "\n"

        self.current_network = new_network
        return output
