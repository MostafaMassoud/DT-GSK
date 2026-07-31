"""CEC2017 visualization and timing utilities.

Provides surface_plot() for 3D visualization and time_batch() for benchmarking.
Both use the batch (M, N) calling convention.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


def surface_plot(
    function: Callable[[np.ndarray], np.ndarray],
    domain: tuple[float, float] = (-100, 100),
    points: int = 30,
    dimension: int = 2,
    ax: object = None,
) -> None:
    """Create a 3D surface plot of a benchmark function.

    Args:
        function: Callable taking (M, N) array, returning (M,) array.
        domain: (min, max) bounds for each dimension.
        points: Grid resolution per axis (total evals = points²).
        dimension: N passed to function. Dims > 2 are set to zero.
        ax: Optional matplotlib Axes with projection='3d'.
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits import mplot3d  # noqa: F401 — registers '3d' projection

    xs = np.linspace(domain[0], domain[1], points)
    X, Y = np.meshgrid(xs, xs)
    grid = np.column_stack([X.ravel(), Y.ravel()])

    if dimension > 2:
        grid = np.concatenate([grid, np.zeros((grid.shape[0], dimension - 2))], axis=1)

    Z = function(grid).reshape(points, points)

    show = ax is None
    if show:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z, cmap='gist_ncar', edgecolor='none')
    ax.set_title(getattr(function, '__name__', 'benchmark'))
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    if show:
        plt.show()


def time_batch(
    function: Callable[[np.ndarray], np.ndarray],
    domain: tuple[float, float] = (-100, 100),
    points: int = 30,
    dimension: int = 2,
) -> float:
    """Return wall-clock seconds to evaluate points² samples in one batch call.

    Args:
        function: Callable taking (M, N) array, returning (M,) array.
        domain: (min, max) bounds.
        points: Grid resolution per axis.
        dimension: Dimensionality N.
    """
    from time import perf_counter

    xs = np.linspace(domain[0], domain[1], points)
    grid = np.column_stack([np.tile(xs, len(xs)), np.repeat(xs, len(xs))])

    if dimension > 2:
        grid = np.concatenate([grid, np.zeros((grid.shape[0], dimension - 2))], axis=1)

    start = perf_counter()
    _ = function(grid)
    return perf_counter() - start
