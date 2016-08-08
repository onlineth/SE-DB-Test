# The majorana Project
---

## File Structure

### Folders

- double\_beta - The place for the double_beta data files
- single\_electron - The place for the single_electron files

### Files

- START.py - The main function that should be executed by the end user
- createDatabase.py - Creates the database with the 3 tables needed for this application
- database.db - The actual SQLite database file
- rebuild_datafile_pool.py - Used to rebuild the DataFile_Pool table. No data files will every be removed from this table but they will be activated/unactivated depending on if they still exist on the file system.
- plot.py - Contains the plotting function

## Database Structure

 - Users
  - UserID
  - FullName
     - Example: Thomas Hein
  - DateTime

 - DataFile_Pool
  - DataFileID
  - Active
     - If 1, then this data file will be used for tests. 0 means that the data file can no longer be found in the filesystem.
  - SD
     - Single=0;Double=1
  - MD5_Hash
  - FileName
  - DateTime
  
 - ResultEntry
  - ResultID
  - UserID
  - DataFileID
  - UserEnrtySD
     - What the user said: Single=0;Double=1
  - CorrectSD
     - WHat the correct answer is: Single=0;Double=1
  - ConfidenceLevel
     - 0-10;0=Not Confident,10=Confident
  - DateTime
  - Notes*
     - Any notes associated
  - LineData
     - Actual list of the 3D segments of the lines


*Not Required

DateTime: **Creation** Date and Time
