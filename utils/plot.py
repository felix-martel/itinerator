import matplotlib.pyplot as plt
import math

def get_vlines(distance, elevation, z_min, step=5, lstyle="--", alpha=0.2):
    ticks = []
    weights = []
    for i in range(1, len(distance)):
        if math.floor(distance[i - 1]) // step != math.floor(distance[i] // step):
            ticks.append(i)
            w = (i - distance[i - 1]) / (distance[i] - distance[i - 1])
            weights.append(w)

    x_lines = list(range(step, math.floor(distance[-1]), step))
    min_lines = [z_min for _ in ticks]
    max_lines = [(t * elevation[i] + (1 - t) * elevation[i - 1]) for i, t in zip(ticks, weights)]
    return x_lines, min_lines, max_lines

def set_axes(x, z, axes, max_diff):
    z_min, z_max = min(z), max(z)
    dz = max_diff - (z_max - z_min)
    y_min = z_min - dz / 2
    y_max = z_max + dz / 2
    if y_min < 0:
        y_max = y_max - y_min
        y_min = 0

    axes.set_ylim([y_min, y_max])
    axes.set_xlim([min(x), max(x)])
    axes.grid(axis="y", linestyle="--", alpha=0.5)

    return y_min, y_max

def set_grid(axes):
    axes.grid(axis="y", linestyle="--", alpha=0.5)
    for side in ["top", "bottom", "right", "left"]:
        axes.spines[side].set_visible(False)