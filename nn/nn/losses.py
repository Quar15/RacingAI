from typing import NamedTuple
import numpy as np


class Loss(NamedTuple):
    """Represents loss returned from a loss function. Contains error calculated from loss function and gradient from its derivative"""

    error: np.ndarray
    gradient: np.ndarray


def mse(expected: np.ndarray, predicted: np.ndarray) -> Loss:
    """Mean Squared Error"""
    return Loss(
        np.mean(np.power(expected - predicted, 2)),
        2 * (predicted - expected) / np.size(expected),
    )


def bce(expected: np.ndarray, predicted: np.ndarray) -> Loss:
    """Binary Cross Entropy"""
    return Loss(
        np.mean(-expected * np.log(predicted) - (1 - expected) * np.log(1 - predicted)),
        ((1 - expected) / (1 - predicted) - expected / predicted) / np.size(expected),
    )
