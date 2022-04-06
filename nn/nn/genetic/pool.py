from copy import deepcopy
from dataclasses import dataclass, field
from os import PathLike
import struct
from typing import Optional
from pathlib import Path
import jsonpickle

import numpy as np
from nn.genetic.pickers import Picker
from nn.layers.base import BaseLayer

from nn.network import NeuralNetwork


@dataclass()
class NetworkPool:
    networks: list[NeuralNetwork]

    picker: Picker

    generation: int = 1

    best_score: float = 0.0
    best_network: NeuralNetwork = None

    def __init__(
        self,
        pool_size: int,
        picker: Picker,
        structure: list[BaseLayer] = None,
        generation: int = 1,
    ):
        self.networks = list()
        self.picker = picker
        self.generation = generation

        if structure is not None:
            self.structure = structure
        else:
            self.structure = list()

        for _ in range(pool_size):
            if len(self.structure) > 0:
                cp = deepcopy(structure)

                for layer in cp:
                    layer.randomize()

                self.networks.append(NeuralNetwork(cp))

    def forward(self, index: int, inputs: np.ndarray) -> np.ndarray:
        return self.networks[index].forward(inputs)

    def forward_all(self, inputs: np.ndarray) -> np.ndarray:
        return np.array(
            [network.forward(inputs[i]) for i, network in enumerate(self.networks)]
        )

    def next_generation(
        self,
        mutation_rate: float,
        perturbing_rate: float,
        fitness: list[float],
        keep_best: int = 1,
    ):
        assert keep_best <= len(self.networks)
        new_networks = list()

        self.picker.set_pool(fitness, self.networks)

        new_networks.extend([n.copy() for n in self.picker.best_n(keep_best)])

        self.best_network = self.picker.best_n(1)[0]
        self.best_score = self.picker.fitnesses[0]

        while len(new_networks) < len(self.networks):
            crossed = self.best_network.copy()
            p1, p2 = self.picker.pick()
            crossed = p1.cross_with(p2)

            if self.picker.fitnesses[1] > 0:
                crossed = p1.cross_with(p2)
            else:
                crossed = p1.copy()

            if np.random.random() < mutation_rate:
                crossed.mutate_network(perturbing_rate)

            new_networks.append(crossed)

        self.networks = new_networks

        self.generation += 1

    @staticmethod
    def from_model(
        model: NeuralNetwork, pool_size: int, picker: Picker
    ) -> "NetworkPool":
        pool = NetworkPool(pool_size, picker)

        for _ in range(pool_size):
            pool.networks.append(deepcopy(model))

        return pool

    @staticmethod
    def from_json(json: str) -> "NetworkPool":
        return jsonpickle.decode(json)

    def to_json(self) -> str:
        return jsonpickle.encode(self)

    @staticmethod
    def from_file(
        file: PathLike, pool_size: int = None, picker: Picker = None
    ) -> "NetworkPool":
        with open(file, "r") as f:
            decoded = NetworkPool.from_json(f.read())

            if Path(file).suffix == ".ntw":
                return NetworkPool.from_model(decoded, pool_size, picker)

            return decoded

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

        target = directory.joinpath(filename + ".ntp")
        mode = "w" if overwrite else "x"

        with open(target, mode) as f:
            f.write(self.to_json())
