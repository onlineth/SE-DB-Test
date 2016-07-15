import plot
import os
import sys
import plotly_plot
import learn_functions

# Old plot function
# import plot

# Double Beta or Single Electron
SD = int(raw_input("Single Electron (0) or Double Beta (1) - 0 or 1\n"))

# Ask for connections
Lines = int(raw_input("Do you want points connected? Yes (1) or No (0)\n"))

DataFilePool = learn_functions.findRandomEntry(SD)

while 1:
    # clears the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Get the file path
    if DataFilePool[0][1]:
        file = 'double_beta/'+str(DataFilePool[0][2])
        print "This is a Double Beta located at "+file
    else:
        file = 'single_electron/'+str(DataFilePool[0][2])
        print "This is a Single Electron located at "+file

    # Get the plot then show it

    # Old plot function
    # the_main_plot = plot.main_plot(file)
    # the_main_plot.show()

    # Best function name ever
    plotly_plot.PlotlyPlotPloter(file, Lines)

    # ask if user wants to continue
    action = raw_input("1. Same type again? [enter]\n2. Different type\n3. Toggle Lines\n4. Quit App\n")

    # Find a new one of the same type
    if (int(action)) == 1 or action == '':
        DataFilePool = learn_functions.findRandomEntry(SD)
    # Switch path type
    if int(action) == 2:
        if SD == 1:
            SD = 0
        else:
            SD = 1
        DataFilePool = learn_functions.findRandomEntry(SD)
    if int(action) == 3:
        if Lines == 1:
            Lines = 0
        else:
            Lines = 1
    # Quit
    if int(action) == 4:
        print "Goodbye"
        sys.exit()
