import os
import database as db

class ClassBook(db.Database):
    def initDatabase(self):
        self.updateTables()
    
    def createDBFile(self, name):
        cwd = os.getcwd()
        filesDir = cwd + '/files/classes'
        databaseFile = filesDir + f'/{name}.db'        

        if not cwd.endswith('gradeBot'):
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile

    def classesList(self):
        return self.tables

    def getClass(self, className):
        try:
            className = ''.join(className.upper().split())
            self.query(f"SELECT *\
                         FROM {className};")
            return self.cur.fetchall()
        except:
            return []

    def printDB(self):
        print(f"ClassBook:\n{self.tables}\n")