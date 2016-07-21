# import timeit
import sys
import sqlite3
import random
import os
import datetime
from datetime import datetime
# import plotly_plot
import plot

# Initial message
print "Please read everything that is printed on this terminal at least once"

# Uses SQLite for the database
# http://sqlitebrowser.org/ is an awesome GUI browser
# Connect to the database (should be in the script directory)
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()

# Get the User ID - if you don't know or need to create one
UserID = int(raw_input("What is your UserID (a number): "))
UserIDInfo = cursor.execute("SELECT * FROM Users WHERE UserID = "+str(UserID)).fetchall()
if UserIDInfo == []:
    sys.exit("Could not find that user")

# Check to be sure by giving them the name of that userid (should be their name)
check_1 = raw_input("You are "+UserIDInfo[0][1]+"\nCorrect? 1 for no, [enter] for yes")
if check_1:
    sys.exit("ok, execute the users.py script to get your user info or add yourself to the list")

print "~~~~~~ Starting Testing ~~~~~~"
print "Each time you submit a prediction, the database is saved"
print "NOTE: Until you quit this application, no one else can share the database"

while 1:
    # clears the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Find an entry that hasn't been tested on this user yet (it's random)
    DataFilePool = cursor.execute("""SELECT DataFileID, SD, FileName
    FROM DataFile_Pool
    WHERE Active = 1 and DataFileID NOT IN (SELECT DataFileID FROM ResultEntry Where UserID = %s)
    ORDER BY RANDOM()
    LIMIT 1""" % (str(UserID))).fetchall()

    # Getting ready
    print "Here is the graph, make a prediction whether it is a single electron or a double beta"
    print "When done close the graph window and follow the prompt"

    # Get the file path
    if DataFilePool[0][1]:
        file = 'double_beta/'+str(DataFilePool[0][2])
    else:
        file = 'single_electron/'+str(DataFilePool[0][2])

    # Get the plot then show it

    # Old plot function
    the_main_plot = plot.main_plot(file)
    the_main_plot.show()

    # Best function name ever
    # plotly_plot.PlotlyPlotPloter(file)

    # At this point the plot window has been closed, let's ask a few questions
    while 1:
        UserEnrtySD = int(input("Is it a single electron(1) or double beta(0)? type 1 or 0\n"))
        ConfidenceLevel = int(input("How confident are you? 0-10, 0 being the lowest-10 being the highest\n"))
        Notes = str(raw_input("Any notes you want to include (this is optional)\nNotes: "))
        if (UserEnrtySD == 1 or UserEnrtySD == 0) and (ConfidenceLevel >= 0 and ConfidenceLevel <= 10):
            break
        else:
            print "Opps, try filling this out again"

    # User entry complete, now insert the data
    cursor.execute("""INSERT INTO ResultEntry (UserID,DataFileID,UserEnrtySD,
    CorrectSD,ConfidenceLevel,DateTime,Notes)
    VALUES (%s,%s,%s,%s,%s,'%s','%s')
    """ % (str(UserID), str(DataFilePool[0][0]), str(UserEnrtySD), str(DataFilePool[0][1]),
           str(ConfidenceLevel), "{:%Y-%m-%d %H:%M}".format(datetime.now()), str(Notes).replace("'", "")))

    # and commit the data
    conn.commit()

    # ask if user wants to continue
    if raw_input("Great, data has been submitted, continue? [enter] for yes, 1 for no\n"):
        print "Goodbye"
        sys.exit()
