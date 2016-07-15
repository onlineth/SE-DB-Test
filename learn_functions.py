import sqlite3
import os
import sys

# Uses SQLite for the database
# http://sqlitebrowser.org/ is an awesome GUI browser
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
