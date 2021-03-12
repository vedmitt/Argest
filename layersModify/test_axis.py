import matplotlib.pyplot as plt
import numpy as np


def setNewAxis():
    plt.figure()
    plt.axis([0, 16, 0, 16])
    plt.grid(False)  # set the grid
    data = [(8, 2, 'USA'), (2, 8, 'CHN')]

    for obj in data:
        plt.text(obj[1], obj[0], obj[2])  # change x,y as there is no view() in mpl

    ax = plt.gca()  # get the axis
    ax.set_ylim(ax.get_ylim()[::-1])  # invert the axis
    ax.xaxis.tick_top()  # and move the X-Axis
    ax.yaxis.set_ticks(np.arange(0, 16, 1))  # set y-ticks
    ax.yaxis.tick_left()  # remove right y-Ticks


if __name__ == "__main__":
    setNewAxis()
