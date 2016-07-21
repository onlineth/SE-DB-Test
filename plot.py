# This file if for plotting the path of the electron
from axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys


def main_plot(file, lineradius=0):
    # Main plot function, returns the plot

    # temp
    # file = 'double_beta/mctruehits_trk_0.dat'

    plot_trks = True

    evt = 0

    vtrk_file = file
    mctrk_file = file
    # print "===>  Event   ",evt + iev_start
    evt += 1

    trktbl = np.loadtxt(vtrk_file)
    vtrk_ID_temp = trktbl[:, 0]
    vtrk_x = trktbl[:, 1]
    vtrk_y = trktbl[:, 2]
    vtrk_z = trktbl[:, 3]
    vtrk_E = trktbl[:, 4]
    print "Found {0} voxels".format(len(vtrk_ID_temp))

    # Convert to integer IDs.
    vtrk_ID = []
    vtrk_neighb = []
    for vid in vtrk_ID_temp:
        vtrk_ID.append(int(vid))
        vtrk_neighb.append([-1])
        # do not know how to create an empty list, insert "someting"

    # Read the MC track.
    mctrktbl = np.loadtxt(mctrk_file)
    mctrk_ID_temp = mctrktbl[:, 0]
    mctrk_x = mctrktbl[:, 1]
    mctrk_y = mctrktbl[:, 2]
    mctrk_z = mctrktbl[:, 3]
    mctrk_E = mctrktbl[:, 4]
    # if(debug > 0): print "Found {0} voxels".format(len(mctrk_ID_temp))

    # Convert to integer IDs.
    mctrk_ID = []
    for mid in mctrk_ID_temp:
        mctrk_ID.append(int(mid))

    if (plot_trks):

        fig = plt.figure(figsize=(20, 10))

        ax3 = fig.add_subplot(111, projection='3d')
        mctrk_col = []
        for energy in mctrk_E:
            mctrk_col.append(1000 * energy)

        psize = 5000 * mctrk_E

        dist = 0
        for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
            point1 = np.array((i, o, p))
            for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
                if i != j and o != k and p != l:
                    point2 = np.array((j, k, l))
                    dist += np.linalg.norm(point1-point2)

        # lineradius = (dist/len(mctrk_x))/10050
        # print lineradius

        for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
            point1 = np.array((i, o, p))
            for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
                if i != j and o != k and p != l:
                    point2 = np.array((j, k, l))
                    dist = np.linalg.norm(point1-point2)
                    if dist < lineradius:
                        ax3.plot([i, j], [o, k], [p, l], linewidth=2, picker=4, c='red', zorder=-1)

        s3 = ax3.scatter(mctrk_x, mctrk_y, mctrk_z, c=psize, cmap='hsv', s=60, zorder=2)

        ax3.set_xlabel("x (mm)")
        ax3.set_ylabel("y (mm)")
        ax3.set_zlabel("z (mm)")

        lb_x = ax3.get_xticklabels()
        lb_y = ax3.get_yticklabels()
        lb_z = ax3.get_zticklabels()
        for lb in (lb_x + lb_y + lb_z):
            lb.set_fontsize(8)

        def on_pick(event):
            event.artist.set_visible(0)
            fig.canvas.draw()

        fig.canvas.callbacks.connect('pick_event', on_pick)
        return plt

# Testing
# main_plot('double_beta/mctruehits_trk_0.dat', 1).show()
