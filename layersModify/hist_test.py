# import tkinter as tk

# from tkinter import *
# from tkinter import ttk
# root = Tk()

# import matplotlib.pyplot as plt
# import numpy as np
#
# rng = np.random.RandomState(10)  # deterministic random data
# a = np.hstack((rng.normal(size=1000),
#                rng.normal(loc=5, scale=2, size=1000)))
# _ = plt.hist(a, bins='auto')  # arguments are passed to np.histogram
# plt.title("Histogram with 'auto' bins")
# plt.show()

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mol = np.random.rand(6, 3) * 10.0

fig3d = plt.figure(figsize=(6.5, 6.5))

fig3d.canvas.set_window_title('3D')

ax3d = fig3d.gca(projection='3d')
ax3d.scatter(mol[:, 0], mol[:, 1], mol[:, 2], s=200)

# List to save your projections to
projections = []


# This is called everytime you release the mouse button
def on_click(event):
    azim, elev = ax3d.azim, ax3d.elev
    projections.append((azim, elev))
    print(azim, elev)


cid = fig3d.canvas.mpl_connect('button_release_event', on_click)

plt.show()
