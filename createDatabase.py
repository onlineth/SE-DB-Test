# Run this file once and never return
import datetime
from datetime import datetime
import sqlite3

# Connect to the database
conn = sqlite3.connect("database.db")

# Get a connection cursor for the database
cursor = conn.cursor()

# ~~~~~~ Create the tables ~~~~~~ #
# Create the DataPool Table
cursor.execute("""CREATE TABLE `DataFile_Pool` (
 `DataFileID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
 `Active` INTEGER NOT NULL,
 `SD` INTEGER NOT NULL,
 `MD5_Hash` TEXT NOT NULL UNIQUE,
 `FileName` TEXT NOT NULL,
 `DateTime` TEXT NOT NULL
)""")

# Create the ResultEnrty Table
cursor.execute("""CREATE TABLE `ResultEntry` (
`ResultID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`UserID`	TEXT NOT NULL,
`DataFileHash`	TEXT NOT NULL,
`UserEnrtySD`	INTEGER NOT NULL,
`CorrectSD`	INTEGER NOT NULL,
`ConfidenceLevel`	INTEGER NOT NULL,
`DateTime`	TEXT NOT NULL,
`Notes`	TEXT,
`LineData`	TEXT
);""")

# Create the Users Table
cursor.execute("""CREATE TABLE "Users" (
 `UserID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
 `FullName` TEXT NOT NULL UNIQUE,
 `DateTime` TEXT NOT NULL
)""")

# Add the anonymous User
cursor.execute("INSERT INTO Users (UserID, FullName, DateTime) VALUES (0, '%s', '%s')" % ('anonymous', "{:%Y-%m-%d %H:%M}".format(datetime.now())))

# Commit the chances so they stick
conn.commit()

# Clossing the connection
conn.close()
