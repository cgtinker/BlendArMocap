import matplotlib.pyplot as plt
import numpy as np


# region clamps
def clamp(n, smallest, largest):
    return np.clip(n, smallest, largest)


def smooth_clamp(n, smallest, largest):
    return smallest + (largest - smallest) * (lambda t: np.where(
        t < 0, 0, np.where(t <= 1, 3 * t ** 2 - 2 * t ** 3, 1)))(
        (n - smallest) / (largest - smallest))


def sigmoid(n, smallest, largest):
    return smallest + (largest - smallest) * (
        lambda t: (1 + 200 ** (-t + 0.5)) ** (-1))((n - smallest) / (largest - smallest))


def clampoid(n, smallest, largest):
    return smallest + (largest - smallest) * (
        lambda t: 0.5 * (1 + 200 ** (-t + 0.5)) ** (-1) + 0.5 * np.where(
            t < 0, 0, np.where(
                t <= 1, 3 * t ** 2 - 2 * t ** 3, 1)))((n - smallest) / (largest - smallest))


# endregion


def polynomial_expansion(n, x, y, offset=0.0):
    n += offset
    return (n + x) * (n + y)


def run():
    inputs = range(0, 10, 1)
    values = [polynomial_expansion(v/10, -1, 2, -.5) for v in inputs]
    plt.plot(values, c="black")
    plt.ylabel('some numbers')
    plt.show()


if __name__ == '__main__':
    run()
