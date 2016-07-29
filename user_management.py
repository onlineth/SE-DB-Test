# This script will list the current users and allow you to create new ones
# It might be a lot easier to use a database browser but this is for your
# convinience.

import sqlite3
import datetime
from datetime import datetime
from tabulate import tabulate


# Connect to the database
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()

# Create the action variable
action = 0
while 1:

    # Commit doesn't happen until you tell it too
    print "Remeber to save (4) BEFORE you stop this script"

    # Get a list of the Users in the database
    UsersList = cursor.execute('SELECT * from Users').fetchall()

    # Add a header to the table
    UsersList = [["UserID", "Full Name", "Date & Time"]]+UsersList

    # Print out the table
    print tabulate(UsersList)

    # Instructions
    print "1. Add a user\n2. Remove a user\n3. Rename a user\n4. Quit and Save\n5. Quit and don't save"
    action = input("Type a number")

    # Add a user
    if action == 1:
        print ("Add a user")
        FullName = str(raw_input("Full Name (must be unique): "))
        cursor.execute("INSERT INTO Users (FullName, DateTime) VALUES ('%s', '%s')" % (FullName, "{:%Y-%m-%d %H:%M}".format(datetime.now())))
        print("Execute the insertation, check if it's in the table;")

    # Remove a user & it's entries
    if action == 2:
        print "REMOVE A USER - This is remove a user AND their entries in the results"
        UserID = input("UserID: ")
        # Remove the user from the Users table
        cursor.execute("DELETE FROM Users WHERE UserID = "+str(UserID))
        # Remove the user's entrues from the ResultEntry table
        cursor.execute("DELETE FROM ResultEntry WHERE UserID = "+str(UserID))
        print "User and it's entries have been removed, double check the table"

    # Rename a user
    if action == 3:
        print("Rename a user")
        UserID = input("UserID: ")
        FullName = raw_input("New Full Name: ")
        cursor.execute("UPDATE Users SET FullName = \""+FullName+"\" WHERE UserID = "+str(UserID))
        print "User has been renamed, double check the table"

    # Quit and save
    if action == 4:
        print "Quitting and saving"
        conn.commit()
        break

    # Quit without saving
    if action == 5:
        print "Quitting without saving"
        break

# All done
print "Goodbye"
