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

    def close(self):
        self.close()
        
class GradeBook(Database):
    def initDatabase(self):
        self.query("CREATE TABLE IF NOT EXISTS Students (uID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                               Name TEXT NOT NULL,\
                                                               CulmulativeGPA REAL DEFAULT 0);")

        self.updateTables()
    
    def printDB(self):
        print(f"Tables:\n{self.tables}\n")
        self.query("SELECT * FROM Students;")
        students = self.cur.fetchall()
        print(f"Students:\n{students}")


class StudentDB(Database):
    def initDatabase(self):
        self.query(f"CREATE TABLE IF NOT EXISTS gpa (sID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                     SemesterGpa REAL NOT NULL DEFAULT 0);")
        
        self.query(f"CREATE TABLE IF NOT EXISTS Semester (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                          Name TEXT NOT NULL,\
                                                          Credits REAL NOT NULL DEFAULT 0,\
                                                          Grade REAL NOT NULL DEFAULT 0);")
                                                        
        self.updateTables()

    def createDBFile(self, name):
        cwd = os.getcwd()
        filesDir = cwd + '/files/students'
        databaseFile = filesDir + f'/{name}.db'        

        if cwd[-8:] != 'gradeBot':
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile
    
    def printDB(self):
        print(f"Tables:\n{self.tables}\n")

class ClassDB(Database):
    def initDatabase(self):
        self.query("CREATE TABLE IF NOT EXISTS Classes  (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                               Name TEXT NOT NULL,\
                                                               Credits REAL NOT NULL DEFAULT 0,\
                                                               UNIQUE(Name));")
        self.updateTables()
    
    def createDBFile(self, name):
        cwd = os.getcwd()
        filesDir = cwd + '/files/classes'
        databaseFile = filesDir + f'/{name}.db'        

        if cwd[-8:] != 'gradeBot':
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile
    
    def printDB(self):
        print(f"Tables:\n{self.tables}\n")


def createStudent(gradeBookDB, name):
    gradeBookDB.query(f"INSERT INTO Students(Name) VALUES('{name}')")
    studentDBName = name.split()[0].lower() + name.split()[1]
    return StudentDB(studentDBName)