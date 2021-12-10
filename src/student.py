import os
import database as db
import commands as cmd
from pprint import pprint

class StudentDB(db.Database):
    #--Public Methods--#
    def getGpaList(self):
        self.query("SELECT *\
                    FROM SemesterGpa;")
        return self.cur.fetchall()
    
    def getSemesterGrades(self):
        semesterNum = int(input('What semester would you like to check? '))
        self.query(f"SELECT ClassName, CurrentGrade\
                     FROM ClassGrades\
                     WHERE SemesterNum = {semesterNum};")
        semesterList = self.cur.fetchall()
        return semesterList if semesterList != [] else f'No grades for semester {semesterNum}...'
    
    def createClass(self, gradeDB, classDB, className, credits, semesterNum):
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName

        classDB.query(f"CREATE TABLE IF NOT EXISTS {classDBName} (aID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                                  AssignmentType TEXT NOT NULL,\
                                                                  PercentOfGrade REAL NOT NULL DEFAULT 0,\
                                                                  DropAmount INTEGER NOT NULL DEFAULT 0);")
        classDB.commit()

        if (classDBName, credits) in gradeDB.getClasses():
            print(f'NOTE: Class already in database...')
        else:
            gradeDB.query(f"INSERT INTO ClassList(Name, Credits) VALUES('{classDBName}', {credits});")
            gradeDB.commit()
            classDB.initClass(className)

        self.query(f"CREATE TABLE IF NOT EXISTS {tableName} (aID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                                  AssignmentType TEXT NOT NULL,\
                                                                  AssignmentName TEXT NOT NULL,\
                                                                  Grade FLOAT NOT NULL DEFAULT 0);")
        self.query(f"INSERT INTO ClassGrades(SemesterNum, ClassName, Credits) VALUES({semesterNum}, '{classDBName}', {credits});")
        self.commit()

    def getClassReport(self, assignmentType=None):
        className   = input('What class would you like a report of? ')
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName
        
        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        if assignmentType == None:
            self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                         FROM Assignments\
                         WHERE ClassName = '{className}';")
            return self.cur.fetchall()
        else:
            self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                         FROM {tableName}\
                         WHERE ClassName = '{className}' AND AssignmentType = '{assignmentType.upper()}';")
            return self.cur.fetchall()

    def addGrade(self, classDB):
        className   = input('What class would you like to add? ')
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

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

        self.query(f"INSERT INTO Assignments (ClassName, AssignmentType, AssignmentName, Grade) VALUES('{className}',\
                                                                                                       '{assignmentType}',\
                                                                                                       '{assignmentName}',\
                                                                                                       {grade});")
        self.commit()

        self._calculateAssignmentAverage(className, assignmentType)

        print("All done... Thanks!")

    def removeAssignment(self):
        className   = input('What class would you like to delete from? ')
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        print("Here's a list of grades...")
        self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                     FROM Assignments;")
        pprint(self.cur.fetchall())

        assignmentName = input("What's the name of the assignment you would like to remove? (Case sensitive) ")
        self.query(f"DELETE\
                     FROM Assignments\
                     WHERE AssignmentName = '{assignmentName}'")
        self.commit()
        
        print("All done... Thanks!")


    def printDB(self):
        print(f"{self.name}:\n{self.tables}\n")

    #--Private Methods--#
    def _initDatabase(self):
        self.query(f"CREATE TABLE IF NOT EXISTS SemesterGpa (SemesterNum INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             SemesterGpa REAL NOT NULL DEFAULT 0);")
        
        self.query(f"CREATE TABLE IF NOT EXISTS ClassGrades (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             SemesterNum INTEGER NOT NULL,\
                                                             ClassName TEXT NOT NULL,\
                                                             Credits FLOAT NOT NULL DEFAULT 0,\
                                                             CurrentGrade FLOAT NOT NULL DEFAULT 0,\
                                                             FinalGrade FLOAT NOT NULL DEFAULT 0);")

        self.query(f"CREATE TABLE IF NOT EXISTS Assignments (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             ClassName TEXT NOT NULL,\
                                                             AssignmentType TEXT NOT NULL,\
                                                             AssignmentName TEXT NOT NULL,\
                                                             Grade REAL NOT NULL DEFAULT 0);")
        self.commit()

    def _createDBFile(self, name):
        cwd          = os.getcwd()
        filesDir     = cwd + '/files/students'
        databaseFile = filesDir + f'/{name}.db'        

        if not cwd.endswith('gradeBot'):
            print('ERROR: Incorrect usage, must execute main.py from gradeBot/ and not from within the src/ directory...')
            exit(1)
        if not os.path.isdir(filesDir):
            os.mkdir(filesDir)
        if not os.path.isfile(databaseFile):
            open(databaseFile, 'w').close()

        return databaseFile

    def _calculateAssignmentAverage(self, className, assignmentType):
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName

        self.query(f"SELECT ROUND(AVG(Grade), 4)\
                     FROM Assignments\
                     WHERE AssignmentType = '{assignmentType}';")

        print(self.cur.fetchall())