# This tool is used to rebuild the "DataFile_Pool" table in the database.
# It will never remove entries but will loop over all the data files and
# check for duplicate hashes in the table. Of course, if there is a duplicate,
# it will not readd the same entry.
# This script should not take long, it can process about 5K per second

# Prints majors events

import sqlite3
import glob
import os
import hashlib
import datetime
from datetime import datetime

# Connect to the database
conn = sqlite3.connect("database.db")
print "Connected to Database"

# Get a connection cursor for the database
cursor = conn.cursor()
print "Created a Cursor"

# get the Script Directory
script_dir = os.path.dirname(__file__)

# Deactivate all filenames then reactivate them as they are found again
# The reason for this is if a data file is deleted, it won't remove it from
# the database but just set it's active attribute to 0
cursor.execute('UPDATE DataFile_Pool SET Active = 0')
print "Reset all the active column"

# Stats Counter to show results of the run at the end
FileandHash = 0
NotFileandHash = 0
AddedFiles = 0

# First go through the double_beta directory and then the single_electron directrory
for zone in ['double_beta', 'single_electron']:
    # Change the current directory to the current zone
    os.chdir(script_dir+"/"+zone)
    print "Changed the directory for "+zone

    # Loop over all the .dat files
    for file in glob.glob("*.dat"):
        # Get the hash of the current file
        hash = hashlib.md5(open(script_dir+'/'+zone+'/'+file).read()).hexdigest()
        # Check if the hash already exists in the table
        if cursor.execute('select FileName from DataFile_Pool WHERE MD5_Hash="'+hash+'"').fetchall():
            # Check to see if the filename and it's hash are in the database together
            if cursor.execute('select FileName from DataFile_Pool WHERE MD5_Hash="'+hash+'" and FileName="'+file+'"').fetchall():
                # It is, so reactivate this data file
                FileandHash += 1
                cursor.execute('UPDATE DataFile_Pool SET Active = 1 WHERE MD5_Hash="'+hash+'" and FileName="'+file+'"')
            else:
                # It isn't (a duplicate hash with a different filename), so don't activate or add anything
                NotFileandHash += 1
        else:
            # What are we dealing with? SE or DB?
            if zone == 'single_electron':
                SD = 0
            else:
                SD = 1
            # Create the entry
            sqlReady = """INSERT INTO DataFile_Pool (Active, SD, MD5_Hash, FileName, DateTime)
            VALUES (%s, %s, '%s', '%s', '%s')""" % (1, SD, hash, file, "{:%Y-%m-%d %H:%M}".format(datetime.now()))
            # Now execute the entry
            cursor.execute(sqlReady)
            AddedFiles += 1

# Print Stats
if NotFileandHash:
    print "Found same hash but couldn't find for "+str(NotFileandHash)+" file(s), each hash is unactive"
if FileandHash:
    print "Found "+str(FileandHash)+" files with the same filename and the same hash, it's been reactivated"
if AddedFiles:
    print "Added "+str(AddedFiles)+" new files and they've been activated."

print "About to commit"
# Wish I knew this command when I started:/ (it then pushes the changes to the database)
conn.commit()
print "Just commited changes, now closing connection"

# Close the connection
conn.close()
