from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import pickle
import numpy as np
from typing_extensions import Self


@dataclass(kw_only=True)
class BaseLayer:
    """Base Layer class from which all layers inherit.
    Should not be instanciated on its own. All derived classes should implement `forward` method."""

    inputs: Optional[np.ndarray] = None
    # outputs: Optional[np.ndarray] = None

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forwards input array through this layer."""
        self.inputs = inputs
        return inputs

    def backward(self, output_gradient: np.ndarray, learning_rate: float) -> np.ndarray:
        raise NotImplementedError

    def randomize(self):
        pass

    def cross_with(self, other: Self) -> Self:
        return self

    def mutate_layer(self, mutation_rate: float):
        pass

    def copy(self) -> Self:
        return deepcopy(self)

    # def to_json(self) -> str:
    #     """Converts layer to json."""
    #     return jsonpickle.encode(self)

    # @classmethod
    # def from_json(cls, json: str) -> Self:
    #     """Loads Layer from json."""
    #     return jsonpickle.decode(json)
