import numpy as np


def binary_step(inputs: np.ndarray, threshhold: float = 0.0) -> np.ndarray:
    norm = lambda n: 0.0 if n < threshhold else 1.0

    vectorized = np.vectorize(norm)

    return vectorized(inputs)


def round_nearest(inputs: np.ndarray) -> np.ndarray:
    return np.round(inputs)


def softmax(inputs: np.ndarray) -> np.ndarray:
    exponentiated = np.exp(inputs)

    return exponentiated / np.sum(exponentiated)
