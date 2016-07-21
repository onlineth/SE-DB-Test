import plot
import os
import sys
# import plotly_plot
import learn_functions
import plot

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

    if Lines:
        lineRadious = input('What radious (try 1 and go from there)\n')
        lineRadious = int(lineRadious)
    else:
        lineRadious = 0

    the_main_plot = plot.main_plot(file, lineRadious)
    the_main_plot.show()

    # Best function name ever
    # plotly_plot.PlotlyPlotPloter(file, Lines)

    # ask if user wants to continue
    action = raw_input("1. Same type again? [enter]\n2. Same one\n3. Different type\n4. Toggle Lines\n5. Quit App\n")
    if action == '':
        action = 1
    # Switch path type
    if int(action) == 1:
        DataFilePool = learn_functions.findRandomEntry(SD)
    elif int(action) == 2:
        # Nothing to do
        print "ok"
    elif int(action) == 3:
        if SD == 1:
            SD = 0
        else:
            SD = 1
        DataFilePool = learn_functions.findRandomEntry(SD)
    elif int(action) == 4:
        if Lines == 1:
            Lines = 0
        else:
            Lines = 1
    # Quit
    elif int(action) == 5:
        print "Goodbye"
        sys.exit()
