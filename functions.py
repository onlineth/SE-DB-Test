# Functions used everywhere
import os
import sqlite3
import sys
import learn_plot
import datetime
from datetime import datetime
import method_plot

# Connect to the database (should be in the script directory)
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()


def findRandomEntry(SD):
    # Find a random entry
    return cursor.execute("""SELECT DataFileID, SD, FileName
    FROM DataFile_Pool
    WHERE Active = 1 and SD = %s
    ORDER BY RANDOM()
    LIMIT 1""" % (str(SD))).fetchall()


def clearTerm():
    # Clears the terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    return 1


def menu(options, title='', breadcrumbs=[]):
    # This is used to create menus
    while 1:
        clearTerm()
        if breadcrumbs != []:
            thecrumbs = ''
            for crumb in breadcrumbs:
                thecrumbs = thecrumbs + str(crumb) + ' -> '
            print thecrumbs+'\n'
        else:
            print '\n'
        if (title != ''):
            print '\033[1mTitle: ' + title + '\033[0m \n'

        counter = 1
        for currentitem in options:
            print str(counter)+'. '+currentitem
            counter += 1
        userInput = raw_input('\nSelection: ')
        if (userInput.isdigit()):
            userInput = int(userInput)
            if (userInput > 0 and userInput < (len(options)+1)):
                return (options[int(userInput)-1])

        raw_input('\nInncorect Input, please try again')
        continue


def learn(SD):
    # Ask for connections
    Lines = int(raw_input("Show actual trajectory? Yes (1) or No (0)\n"))

    DataFilePool = findRandomEntry(SD)

    # Get the file path
    if DataFilePool[0][1]:
        file = 'double_beta/'+str(DataFilePool[0][2])
        print "This is a Double Beta located at "+file
    else:
        file = 'single_electron/'+str(DataFilePool[0][2])
        print "This is a Single Electron located at "+file

    the_main_plot = learn_plot.learn_plot(file, Lines)
    the_main_plot.show()


def user():
    # Enter a Name
    username = raw_input('Please enter a name for the profile to used. Use \'0\' to be anonymous\nProfile Name: ')
    if (username == '0'):
        raw_input("ok, this session until you come back here will be anonymous.\n[Click Enter]")
        return 0
    UserIDInfo = cursor.execute("SELECT * FROM Users WHERE fullname = '"+str(username)+"'").fetchall()
    if UserIDInfo == []:
        cursor.execute("INSERT INTO Users (FullName, DateTime) VALUES ('%s', '%s')" % (username, "{:%Y-%m-%d %H:%M}".format(datetime.now())))
        print("The profile name you entered does not exist in the database, so it has been registered automatically for you.")
        UserIDInfo = cursor.execute("SELECT * FROM Users WHERE fullname = '"+str(username)+"'").fetchall()
    UserID = UserIDInfo[0][0]
    raw_input("You, "+username+", have been logged in and your ID is: "+str(UserID)+'.\n[Click Enter]')

    # and commit the data
    conn.commit()

    return UserID


def examine():
    while 1:
        graphID = raw_input('What is the graph ID?\n')
        if (graphID.isdigit() == 0):
            raw_input("Incorrect Input, try again (should be an integer above 0)\n[Click Enter]")
        else:
            break
    FileHash = (cursor.execute("""SELECT DataFileHash
    FROM ResultEntry
    WHERE ResultID = %s
    """ % (str(graphID))).fetchall())[0][0]

    PlotInfo = (cursor.execute("""SELECT DataFileID, SD, FileName, MD5_Hash
        FROM DataFile_Pool
        WHERE Active = 1 and MD5_Hash = '%s'""" % (FileHash)).fetchall())[0]

    # Get the file path
    if PlotInfo[1]:
        file = 'double_beta/'+str(PlotInfo[2])
    else:
        file = 'single_electron/'+str(PlotInfo[2])

    # Now actually plot it
    method_plot.main(file, ['Root', 'Mode', 'Examine'])

    return 1
