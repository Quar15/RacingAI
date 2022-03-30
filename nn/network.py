from copy import deepcopy
from dataclasses import dataclass
from itertools import pairwise
from os import PathLike
from pathlib import Path
from typing import Iterator, Optional

import jsonpickle
import numpy as np
from typing_extensions import Self

from nn.layers import BaseLayer, Dense
from nn.layers.activators import ActivationLayer
from nn.normalizators import softmax


@dataclass()
class NeuralNetwork:
    layers: list[BaseLayer]

    input_count: int

    def __init__(self, layers: list[BaseLayer]) -> None:
        # assert len(layers) >= 3, "At least 3 layers required"
        assert isinstance(layers[0], Dense), "First layer should be a dense layer"

        self.layers = layers
        self.input_count = layers[0].weights.shape[1]

    @staticmethod
    def from_counts(
        neuron_counts: list[int],
        activators: list[ActivationLayer],
    ) -> "NeuralNetwork":
        assert len(neuron_counts) >= 3, "At least 3 layers required"
        assert len(neuron_counts) == len(
            activators
        ), "Each layer needs an activation function"

        layers = list()

        for counts, activator in zip(pairwise(neuron_counts), activators):
            layers.append(Dense(*counts))
            layers.append(activator)

        layers.append(activator[-1])

        return NeuralNetwork(layers)

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        output = np.reshape(inputs, (self.input_count, 1))

        for i, layer in enumerate(self.layers):
            output = layer.forward(output)

        return output

    def backward(self, output_error: np.ndarray, learning_rate: float):
        input_error = output_error

        for layer in reversed(self.layers):
            input_error = layer.backward(input_error, learning_rate)

    def cross_with(self, other: Self) -> Self:
        return NeuralNetwork(
            [
                np.random.choice([l1.copy(), l2.copy()])
                for l1, l2 in zip(self.layers, other.layers)
            ]
        )

    def mutate_network(self, perturbing_rate: float):
        chosen_layer = np.random.choice(
            list(filter(lambda l: isinstance(l, Dense), self.layers))
        )

        chosen_layer.mutate_layer(perturbing_rate)

    def copy(self) -> "NeuralNetwork":
        return NeuralNetwork(deepcopy(self.layers))

    def to_json(self) -> str:
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json: str) -> "NeuralNetwork":
        return jsonpickle.decode(json)

    def to_file(
        self,
        filename: str,
        directory: Optional[PathLike] = None,
        create_parents: bool = False,
        overwrite: bool = True,
    ):
        directory = Path.cwd() if directory is None else Path(directory)

        if not directory.exists():
            directory.mkdir(parents=create_parents)

        elif not directory.is_dir():
            raise NotADirectoryError

        target = directory.joinpath(filename + ".ntw")
        mode = "w" if overwrite else "x"

        with open(target, mode) as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(file: PathLike) -> "NeuralNetwork":
        with open(file, "r") as f:
            return NeuralNetwork.from_json(f.read())

    def __iter__(self) -> Iterator[BaseLayer]:
        return iter(self.layers)
