import sqlite3
import plot
import os
import sys

# Uses SQLite for the database
# http://sqlitebrowser.org/ is an awesome GUI browser
# Connect to the database (should be in the script directory)
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()

# Double Beta or Single Electron
SD = int(raw_input("Single Electron (0) or Double Beta (1) - 0 or 1\n"))

while 1:
    # clears the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Find a random entry
    DataFilePool = cursor.execute("""SELECT DataFileID, SD, FileName
    FROM DataFile_Pool
    WHERE Active = 1 and SD = %s
    ORDER BY RANDOM()
    LIMIT 1""" % (str(SD))).fetchall()

    # Get the file path
    if DataFilePool[0][1]:
        print "This is a Double Beta"
        file = 'double_beta/'+str(DataFilePool[0][2])
    else:
        print "This is a Single Electron"
        file = 'single_electron/'+str(DataFilePool[0][2])

    # Get the plot then show it
    the_main_plot = plot.main_plot(file)
    the_main_plot.show()

    # ask if user wants to continue
    action = raw_input("Another of the same type? [enter] for yes, 1 for no, and 2 to quit this application\n")
    if action:
        if int(action) == 2:
            print "Goodbye"
            sys.exit()
        if int(action) == 1:
            if SD == 1:
                SD = 0
            else:
                SD = 1
