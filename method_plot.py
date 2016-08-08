# File only used for scan & examine
from axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys
import functions
import subplotmethods
import ast


def main(file, breadcrumbs, old_data=0):

    # Read the MC track.
    mctrktbl = np.loadtxt(file)
    mctrk_ID_temp = mctrktbl[:, 0]
    mctrk_x = mctrktbl[:, 1]
    mctrk_y = mctrktbl[:, 2]
    mctrk_z = mctrktbl[:, 3]
    mctrk_E = mctrktbl[:, 4]

    # Convert to integer IDs.
    mctrk_ID = []
    for mid in mctrk_ID_temp:
        mctrk_ID.append(int(mid))

    # Create the actual figure
    fig = plt.figure(figsize=(20, 10))

    if (old_data == 0):
        # Init choice var
        choice = 1

        # Make it interactive
        plt.ion()

        # !!!!!! Add your method to the menu

        # Variabls equal to 0
        based_radius = False
        based_shortestDistance = False

        # Points only are default
        print "There will always be one graph that includes just the points"

        # Loop over a list
        while choice != 'Create Graph':
            # Create a list options and their states
            option_1 = 'Radius Based: '+str(based_radius)
            option_2 = 'Shortest Distance Based: '+str(based_shortestDistance)

            # !!!!!! END

            options = [option_1, option_2, 'Create Graph']
            choice = functions.menu(options, 'Plotting Method', breadcrumbs)

            if (choice == option_1):
                based_radius = not based_radius

            if (choice == option_2):
                based_shortestDistance = not based_shortestDistance

        # Clear the terminal
        functions.clearTerm()

        # For all the options, loopover them, see what was chosen, and get those specfic methods in a list
        wanted_options = []
        for option in options:
            if option[-4:] == 'True':
                wanted_options.append(option[:-6])

        # !!!! Make sure number of subplot layouts are under the grand total

        # ok, let's provide some general layouts in the form of lists
        # Currently, this accounts for up to 4 subplots
        option_length = len(wanted_options)+1
        if option_length == 1:
            layout_sub = [111]
        elif option_length == 2:
            layout_sub = [121, 122]
        elif option_length == 3:
            layout_sub = [131, 132, 133]
        elif option_length == 4:
            layout_sub = [121, 122, 221, 222]

        # !!!! END

        # Add the first one be default
        ax3 = fig.add_subplot(layout_sub[0], projection='3d')
        mctrk_col = []
        for energy in mctrk_E:
            mctrk_col.append(1000 * energy)

        psize = 5000 * mctrk_E

        # Remove first from layout
        layout_sub.pop(0)

        # Adds lables and **points**
        endSubUp(ax3, mctrk_x, mctrk_y, mctrk_z, mctrk_E, psize)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Methods are initialized here

        if based_radius:
            based_radius_data = subplotmethods.based_radius(mctrk_x, mctrk_y, mctrk_z)
            based_radius_ax = fig.add_subplot(layout_sub[0], projection='3d',
                                              sharex=ax3, sharey=ax3, sharez=ax3)
            layout_sub.pop(0)
            endSubUp(based_radius_ax, mctrk_x, mctrk_y,
                     mctrk_z, mctrk_E, psize, based_radius_data, "option1")

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END

        def on_pick(event):
            temp_label = event.artist.get_label()
            if temp_label[:6] == "option":

                # !!!!!!!!!!!!!!!!!!! Start

                if temp_label[:7] == "option1":
                    remove_item = ast.literal_eval(temp_label[7:])
                    based_radius_data.remove(remove_item)

                # !!!!!!!!!!!!!!!!!!! End

            event.artist.set_visible(0)
            fig.canvas.draw()

        fig.canvas.callbacks.connect('pick_event', on_pick)

        # Everything is ready to show, so let's do just that
        plt.show()

        # Reminder
        print "DO NOT CLOSE The Graph - It will do it for you\n"

        # Add the continue to test/menu choice
        c_and_c = "Close and Continue"
        wanted_options.append(c_and_c)

        # okay, now we need to provide an options menu, this will simply go call the stuff above
        while choice != c_and_c:
            # Give info message
            print "Note: As you click on the red lines, they will be removed form the graph."

            # Choose an option
            choice = functions.menu(wanted_options, "Reconfigure Subplots", [])

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # Reconfigure subplot section, include a message if nothing
            if (choice == 'Radius Based'):
                based_radius_ax.clear()
                based_radius_data = subplotmethods.based_radius(mctrk_x, mctrk_y, mctrk_z)
                endSubUp(based_radius_ax, mctrk_x, mctrk_y, mctrk_z, mctrk_E, psize, based_radius_data)

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END

        # Add the close to choose subplot save menu
        del wanted_options[-1]
        c_and_c = "Don't pick any of them"
        wanted_options.append(c_and_c)

        # Choose an option
        choice = functions.menu(wanted_options, "Choose subplot to save", [])

        # Init save data list
        save_data = []

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Save the data of a specific subplot section
        if (choice == 'Radius Based'):
            save_data = based_radius_data

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END

        # Close the plot, were finally done
        plt.close()

        # Return the data set
        return save_data

    else:
        ax3 = fig.add_subplot(121, projection='3d')
        mctrk_col = []
        for energy in mctrk_E:
            mctrk_col.append(1000 * energy)

        psize = 5000 * mctrk_E

        endSubUp(ax3, mctrk_x, mctrk_y, mctrk_z, mctrk_E, psize)

        data_ax = fig.add_subplot(122, projection='3d',
                                  sharex=ax3, sharey=ax3, sharez=ax3)

        endSubUp(data_ax, mctrk_x, mctrk_y,
                 mctrk_z, mctrk_E, psize, old_data)
        print "Close the plot when done"
        plt.show()
        return 0


def endSubUp(ax, mctrk_x, mctrk_y, mctrk_z, mctrk_E, psize, data=0, axname=0):

    if data:
        for x in data:
            # If there is a label, use it along with the coordinate of the line
            if axname:
                ax.plot([x[0][0], x[0][1]], [x[1][0], x[1][1]], [x[2][0], x[2][1]],
                        linewidth=2, picker=10, c='red', zorder=-1, label=axname+str(x))
            else:
                ax.plot([x[0][0], x[0][1]], [x[1][0], x[1][1]], [x[2][0], x[2][1]],
                        linewidth=2, picker=10, c='red', zorder=-1)

    ax.scatter(mctrk_x, mctrk_y, mctrk_z, c=psize, cmap='hsv', s=60, zorder=2)

    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")

    lb_x = ax.get_xticklabels()
    lb_y = ax.get_yticklabels()
    lb_z = ax.get_zticklabels()
    for lb in (lb_x + lb_y + lb_z):
        lb.set_fontsize(8)
    return 1
