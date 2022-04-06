from dataclasses import dataclass
import numpy as np
from nn.layers.base import BaseLayer


@dataclass()
class ActivationLayer(BaseLayer):
    """Base activation layer class. Should not be instantiated. All derived classes should implement `activate` and `derivative` methods."""

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        super().forward(inputs)
        vectorized = np.vectorize(self.activate)

        return vectorized(inputs)

    def backward(self, output_gradient: np.ndarray, learning_rate: float) -> np.ndarray:
        vectorized = np.vectorize(self.derivative)

        return np.multiply(output_gradient, vectorized(self.inputs))

    def activate(self, val: float) -> float:
        raise NotImplementedError

    def derivative(self, val: float) -> float:
        raise NotImplementedError


@dataclass()
class Linear(ActivationLayer):
    """Range(-inf, inf)"""

    def activate(self, val: float) -> float:
        return val

    def derivative(self, val: float) -> float:
        return 1


@dataclass()
class Logistic(ActivationLayer):
    """Range(0,1)"""

    def activate(self, val: float) -> float:
        return 1 / (1 + np.exp(-val))

    def derivative(self, val: float) -> float:
        return np.exp(-val) / np.power((np.exp(-val) + 1), 2)


@dataclass()
class Tanh(ActivationLayer):
    """Range(-1,1)"""

    def activate(self, val: float) -> float:
        return (np.exp(val) - np.exp(-val)) / (np.exp(val) + np.exp(-val))

    def derivative(self, val: float) -> float:
        return 1 - np.power(np.tanh(val), 2)


@dataclass()
class ReLU(ActivationLayer):
    """Range(0,inf)"""

    def activate(self, val: float) -> float:
        return max(0, val)

    def derivative(self, val: float) -> float:
        return 0 if val <= 0 else 1


@dataclass()
class ParametricReLU(ActivationLayer):
    """Range(-inf,inf)"""

    slope: float = 0.1

    def activate(self, val: float) -> float:
        return max(self.slope * val, val)

    def derivative(self, val: float) -> float:
        return self.slope if self.slope * val <= val else 1


@dataclass()
class ELU(ActivationLayer):
    """Range(-inf, inf)"""

    slope: float = 1

    def activate(self, val: float) -> float:
        return val if val >= 0 else self.slope * (np.exp(val) - 1)

    def derivative(self, val: float) -> float:
        return 1 if val >= 0 else self.slope * np.exp(val)


@dataclass()
class Swish(ActivationLayer):
    """Range(-inf, inf)"""

    def activate(self, val: float) -> float:
        return val / (1 + np.exp(-val))

    def derivative(self, val: float) -> float:
        return ((np.exp(-val) * val) / np.power((np.exp(-val) + 1), 2)) + (
            1 / (np.exp(-val) + 1)
        )


@dataclass()
class SELU(ActivationLayer):
    """Range(-inf, inf)"""

    slope: float = 1.0

    def activate(self, val: float) -> float:
        return val if val >= 0 else self.slope * (np.exp(val) - 1)

    def derivative(self, val: float) -> float:
        return val if val >= 0 else self.slope * np.exp(val)
