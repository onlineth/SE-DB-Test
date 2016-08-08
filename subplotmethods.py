from axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys
import functions


def based_radius(mctrk_x, mctrk_y, mctrk_z):

    print "\nRadius Based Configuration\n"

    # Get an input (and make sure it's a number or decimal)
    while 1:
        lineradius = raw_input('What would you like the radius to be for the Radius Based graphing method? Try 1 and go from there\nRadius: ')
        try:
            x = float(lineradius)
        except ValueError:
            print "Inncorrect input"
            continue
        break

    return_temp = []

    dist = 0
    for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
        point1 = np.array((i, o, p))
        for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
            if i != j and o != k and p != l:
                point2 = np.array((j, k, l))
                dist += np.linalg.norm(point1-point2)

    for i, o, p in zip(mctrk_x, mctrk_y, mctrk_z):
        point1 = np.array((i, o, p))
        for j, k, l in zip(mctrk_x, mctrk_y, mctrk_z):
            if i != j and o != k and p != l:
                point2 = np.array((j, k, l))
                dist = np.linalg.norm(point1-point2)
                if float(dist) < float(lineradius):
                    return_temp.append([[i, j], [o, k], [p, l]])

    # Clear the terminal
    functions.clearTerm()

    # Return the return data
    return return_temp
