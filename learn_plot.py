# This file if for plotting the path of the electron
# File only used for learning
from axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys


def learn_plot(file, realtrajectory):
    # Main plot function, returns the plot
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

    fig = plt.figure(figsize=(20, 10))

    ax3 = fig.add_subplot(111, projection='3d')
    mctrk_col = []
    for energy in mctrk_E:
        mctrk_col.append(1000 * energy)

    psize = 5000 * mctrk_E

    # This is the place to add subplots
    # If real trajectory, don't use any other type except this
    if (realtrajectory):
        c = 0
        for ignore in mctrk_x:
            if (c + 1 != len(mctrk_x)):
                ax3.plot([mctrk_x[c], mctrk_x[c+1]], [mctrk_y[c], mctrk_y[c+1]], [mctrk_z[c],
                         mctrk_z[c+1]], linewidth=2, picker=4, c='red', zorder=-1)
            c += 1

    s3 = ax3.scatter(mctrk_x, mctrk_y, mctrk_z, c=psize, cmap='hsv', s=60, zorder=2)

    ax3.set_xlabel("x (mm)")
    ax3.set_ylabel("y (mm)")
    ax3.set_zlabel("z (mm)")

    lb_x = ax3.get_xticklabels()
    lb_y = ax3.get_yticklabels()
    lb_z = ax3.get_zticklabels()
    for lb in (lb_x + lb_y + lb_z):
        lb.set_fontsize(8)

    return plt
