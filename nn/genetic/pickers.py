from dataclasses import dataclass, field
import random

import numpy as np

from nn.network import NeuralNetwork


@dataclass()
class Picker:
    fitnesses: list[float] = field(default_factory=list)
    pool: list[NeuralNetwork] = field(default_factory=list)

    def set_pool(self, fitness: list[float], networks: list[NeuralNetwork]):
        self.clear()
        for fit, network in sorted(
            (zip(fitness, networks)), key=lambda x: x[0], reverse=True
        ):
            self.fitnesses.append(fit)
            self.pool.append(network)

        self.fitnesses = self.fitnesses[:len(self.fitnesses)//2]
        self.pool = self.pool[:len(self.pool)//2]

    def clear(self):
        self.fitnesses.clear()
        self.pool.clear()

    def pick(self) -> tuple[NeuralNetwork, NeuralNetwork]:
        pass

    def best_n(self, n: int) -> list[NeuralNetwork]:
        return self.pool[:n]


@dataclass()
class RandomPicker(Picker):
    def pick(self) -> tuple[NeuralNetwork, NeuralNetwork]:
        n1, n2 = random.choices(self.pool, k=2)
        return (n1, n2)


@dataclass()
class WeightedPicker(Picker):
    def pick(self) -> tuple[NeuralNetwork, NeuralNetwork]:
        min_fitness = min(self.fitnesses)
        weights = np.asarray(self.fitnesses)
        if min_fitness < 0:
            weights += -min_fitness + 0.01
        n1, n2 = random.choices(self.pool, weights.tolist(), k=2)
        return (n1, n2)


@dataclass()
class BestPicker(Picker):
    def pick(self) -> tuple[NeuralNetwork, NeuralNetwork]:
        n1, n2 = self.best_n(2)
        return (n1, n2)
