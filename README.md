# The majorana Project
---

## File Structure

### Folders

- double_beta - The place for the double_beta data files
- single_electron - The place for the single_electron files

### Files

- createDatabase.py - Creates the database with the 3 tables needed for this application
- database.db - The actual SQLite database file
- **learn.py** - A place to give any user random plots of their choosing (single or double) to help them learn what types of paths look like
- plot.py - Contains the plotting function
- plot.pyc - Temporary plotting data, can be ignored
- rebuild_datafile_pool.py - Used to rebuild the DataFile_Pool table. No data files will every be removed from this table but they will be activated/unactivated depending on if they still exist on the file system.
- **test.py** - A script that will test the user by providing random electron paths and asking them to discern whether they are the path of a double beta or a single electron.
- **users.py** - User mangement script, can: add, remove, and rename users.


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


*Not Required

DateTime: **Creation** Date and Time
