import os
import sqlite3

class Database:
    def __init__(self, name):
        self.name = name
        self._dbLocation = self._createDBFile(self.name) # unsure if needed
        self.con = sqlite3.connect(self._dbLocation)
        self.cur = self.con.cursor()
        self.tables = []
        self._initDatabase()

    #--Public Methods--#
    def printDB(self):
        print(self.tables)

    def query(self, command):
        self.cur.execute(command)

    def commit(self):
        self.con.commit()
        self._updateTables()
    
    #--Private Methods--#
    def _createDBFile(self, name):
        cwd = os.getcwd()
        filesDir = cwd + '/files'
        databaseFile = filesDir + f'/{name}.db'        

        if not cwd.endswith('gradeBot'):
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile

    # Possibly obsolete?
    def _updateTables(self):
        self.tables = []
        self.query("SELECT name\
                    FROM sqlite_schema\
                    WHERE type='table' AND name NOT LIKE '%sqlite_%';")
        rawTables = self.cur.fetchall()
        for table in rawTables:
            self.tables.append(table[0])
         
    def _initDatabase(self):
        print("\nInitialized base class\n")
        self.updateTables()