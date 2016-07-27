from axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys


def main():
    # Start Showing a list
    pass

# dist = 0
# for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
#     point1 = np.array((i, o, p))
#     for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
#         if i != j and o != k and p != l:
#             point2 = np.array((j, k, l))
#             dist += np.linalg.norm(point1-point2)

# for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
#     point1 = np.array((i, o, p))
#     for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
#         if i != j and o != k and p != l:
#             point2 = np.array((j, k, l))
#             dist = np.linalg.norm(point1-point2)
#             if dist < lineradius:
#                 ax3.plot([i, j], [o, k], [p, l], linewidth=2, picker=4, c='red', zorder=-1)
