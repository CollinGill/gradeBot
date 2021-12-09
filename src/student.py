import os
import database as db
import commands as cmd
from pprint import pprint

class StudentDB(db.Database):
    def initDatabase(self):
        self.query(f"CREATE TABLE IF NOT EXISTS Gpa (SemesterNum INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                     SemesterGpa REAL NOT NULL DEFAULT 0);")
        
        self.query(f"CREATE TABLE IF NOT EXISTS Semester (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                          SemesterNum INTEGER NOT NULL,\
                                                          Name TEXT NOT NULL,\
                                                          Credits REAL NOT NULL DEFAULT 0,\
                                                          Grade REAL NOT NULL DEFAULT 0);")
        self.commit()

    def createDBFile(self, name):
        cwd = os.getcwd()
        filesDir = cwd + '/files/students'
        databaseFile = filesDir + f'/{name}.db'        

        if not cwd.endswith('gradeBot'):
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile
    
    def getGpaList(self):
        self.query("SELECT *\
                    FROM Gpa;")
        return self.cur.fetchall()
    
    def getSemesterGrades(self, semesterNum):
        self.query(f"SELECT Name, Grade\
                    FROM Semester\
                    WHERE SemesterNum = {semesterNum};")
        semesterList = self.cur.fetchall()
        return semesterList if semesterList != [] else 'No grades for this semester...'


    def addGrade(self, classDB, className):
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName

        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        print("Current Class Assignments:")
        classStats = []
        temp = cmd.getClassStats(classDB, className)
        for assignment in temp:
            classStats.append(assignment[1])
        
        pprint(classStats)

        print("\nGrade Information:")
        assignmentName = input("What is the name of the assignment? ")
        assignmentType = input("What is the type of the assignment? ").upper()
        grade          = input("What is the grade of the assignment? ") 

        if assignmentType.upper() not in classStats:
            print(f"ERROR: {assignmentType} not in {classDBName}...")
            return

        self.query(f"INSERT INTO {tableName}(AssignmentType, AssignmentName, Grade) VALUES('{assignmentType}',\
                                                                                           '{assignmentName}',\
                                                                                            {grade});")
        self.commit()
        print("All done... Thanks!")

    def getClassReport(self, className, assignmentType=None):
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName
        
        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        if assignmentType == None:
            self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                         FROM {tableName};")
            return self.cur.fetchall()
        else:
            self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                         FROM {tableName}\
                         WHERE AssignmentType = '{assignmentType.upper()}';")
            return self.cur.fetchall()

    def printDB(self):
        print(f"\t{self.name}:\n{self.tables}\n")