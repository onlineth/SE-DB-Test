import sys
import sqlite3
import random
import os
import datetime
from datetime import datetime
import functions
import plot

# Uses SQLite for the database
# http://sqlitebrowser.org/ is an awesome GUI browser
# Connect to the database (should be in the script directory)
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()


def test(UserID):
    while 1:
        # clears the terminal
        functions.clearTerm()

        # Find an entry that hasn't been tested on this user yet (it's random)
        DataFilePool = cursor.execute("""SELECT DataFileID, SD, FileName, MD5_Hash
        FROM DataFile_Pool
        WHERE Active = 1 and MD5_Hash NOT IN (SELECT DataFileHash FROM ResultEntry Where UserID = %s)
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
        the_main_plot = plot.main_plot(file)
        the_main_plot.show()

        # At this point the plot window has been closed, let's ask a few questions
        while 1:
            UserEnrtySD = int(input("Is it a single electron(0) or double beta(1)? type 0 or 1\n"))
            ConfidenceLevel = int(input("How confident are you? 0-10, 0 being the lowest-10 being the highest\n"))
            Notes = str(raw_input("Any notes you want to include (this is optional)\nNotes: "))
            if (UserEnrtySD == 1 or UserEnrtySD == 0) and (ConfidenceLevel >= 0 and ConfidenceLevel <= 10):
                break
            else:
                print "Opps, try filling this out again"

        # User entry complete, now insert the data
        cursor.execute("""INSERT INTO ResultEntry (UserID,DataFileHash,UserEnrtySD,
        CorrectSD,ConfidenceLevel,DateTime,Notes)
        VALUES (%s,'%s',%s,%s,%s,'%s','%s')
        """ % (str(UserID), str(DataFilePool[0][3]), str(UserEnrtySD), str(DataFilePool[0][1]),
               str(ConfidenceLevel), "{:%Y-%m-%d %H:%M}".format(datetime.now()), str(Notes).replace("'", "")))

        # and commit the data
        conn.commit()

        # Give an ID
        print "Your ID for the last graph is: "+str(cursor.lastrowid)

        # ask if user wants to continue
        if (raw_input("Great, data has been submitted, continue with test? [enter] for yes, 0 for no\n")) == '0':
            return 1
