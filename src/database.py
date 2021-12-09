import os
import sqlite3

class Database:
    def __init__(self, name):
        self.name = name
        self.dbLocation = self.createDBFile(self.name) # unsure if needed
        self.con = sqlite3.connect(self.dbLocation)
        self.cur = self.con.cursor()
        self.tables = []
        self.initDatabase()
    
    def createDBFile(self, name):
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
    
    def updateTables(self):
        self.tables = []
        self.query("SELECT name\
                    FROM sqlite_schema\
                    WHERE type='table' AND name NOT LIKE '%sqlite_%';")
        rawTables = self.cur.fetchall()
        for table in rawTables:
            self.tables.append(table[0])
         
    def printDB(self):
        print(self.tables)
    
    def initDatabase(self):
        print("\nInitialized base class\n")
        self.updateTables()

    def query(self, command):
        self.cur.execute(command)

    def commit(self):
        self.con.commit()
        self.updateTables()
