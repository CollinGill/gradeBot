import os
import sqlite3

class Database:
    def __init__(self, name):
        self.name = name
        self.dbLocation = self.createDBFile()
        self.con = sqlite3.connect(self.dbLocation)
        self.cur = self.con.cursor()
    
    def createDBFile(self):
        cwd = os.getcwd()
        filesDir = cwd + '/files'
        databaseFile = filesDir + f'/{self.name}.db'        

        if cwd[-8:] != 'gradeBot':
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile