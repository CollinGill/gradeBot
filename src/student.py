import os
import database as db
import commands as cmd
from pprint import pprint

# This class connects to the ClassBook database
# This database several tables of data pertain only to the individual student: SemesterGpas, Assignments, Grades in a class
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
    
    def addClass(self, gradeDB, classDB):
        className = input("What class would  you like to add? (Please use the class code, ex. 'MATH 250') ")
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName

        credits = float(input("How many credits do you get from this class? "))
        semesterNum = int(input("During which semester are you taking this class? "))

        self.query(f"CREATE TABLE IF NOT EXISTS {tableName} (aID            INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             AssignmentType TEXT NOT NULL,\
                                                             PercentOfGrade INTEGER NOT NULL DEFAULT 0,\
                                                             Grade          FLOAT NOT NULL DEFAULT -1);")
        self.query(f"INSERT INTO ClassGrades(SemesterNum, ClassName, Credits) VALUES({semesterNum}, '{classDBName}', {credits});")
        self.commit()

        classDB.createClass(gradeDB, className, credits, semesterNum)
        
        assignments = cmd.getClassStats(classDB, className)
        for assignment in assignments:
            self.query(f"INSERT INTO {self.name + classDBName}(AssignmentType, PercentOfGrade) VALUES('{assignment[1]}', {assignment[2]});")
        self.commit()

    # Returns a list of Assignments and their grades from a given class
    def getClassAssignments(self, assignmentType=None):
        className   = input('What class would you like a report of? ')
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

        assignmentType = input("What assignment type would you like to check? (Type 'None' for all assignments)? ").upper()
        
        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        if assignmentType == "NONE":
            self.query(f"SELECT *\
                         FROM Assignments\
                         WHERE ClassName = '{classDBName}';")
            return self.cur.fetchall()
        else:
            self.query(f"SELECT *\
                         FROM Assignments\
                         WHERE ClassName = '{classDBName}' AND AssignmentType = '{assignmentType}';")
            return self.cur.fetchall()

    def addGrade(self, classDB):
        className   = input('What class would you like to add a grade to? ')
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
        assignmentName = input("What is the name of the assignment? ").strip()
        assignmentType = input("What is the type of the assignment? ").strip().upper()
        grade          = float(input("What is the grade of the assignment? "))

        if assignmentType not in classStats:
            print(f"ERROR: {assignmentType} not in {classDBName}...")
            return

        self.query(f"INSERT INTO Assignments (ClassName, AssignmentType, AssignmentName, Grade) VALUES('{classDBName}',\
                                                                                                       '{assignmentType}',\
                                                                                                       '{assignmentName}',\
                                                                                                       {grade});")
        self.commit()

        self._calculateAssignmentAverage(classDB, classDBName, assignmentType)

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

    def updateAssignment(self):
        pass


    def printDB(self):
        print(f"{self.name}:\n{self.tables}\n")

    #--Private Methods--#
    def _initDatabase(self):
        self.query(f"CREATE TABLE IF NOT EXISTS SemesterGpa (SemesterNum INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             SemesterGpa REAL NOT NULL DEFAULT 0);")
        
        self.query(f"CREATE TABLE IF NOT EXISTS ClassGrades (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             SemesterNum INTEGER NOT NULL,\
                                                             ClassName TEXT NOT NULL,\
                                                             Credits REAL NOT NULL DEFAULT 0,\
                                                             CurrentGrade REAL NOT NULL DEFAULT 0,\
                                                             FinalGrade REAL NOT NULL DEFAULT 0);")

        self.query(f"CREATE TABLE IF NOT EXISTS Assignments (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             ClassName TEXT NOT NULL,\
                                                             AssignmentType TEXT NOT NULL,\
                                                             AssignmentName TEXT NOT NULL,\
                                                             Grade REAL NOT NULL DEFAULT -1);")
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

    def _deleteClass(self):
        className = input("What class would you like to purge? ")
        classDBName = ''.join(className.upper().split())
        confirmation = input(f"Are you sure you want to purge {classDBName}? (y/n) ").upper()

        if confirmation == "Y":
            try:
                self.query(f"DELETE\
                             FROM Assignments\
                             WHERE ClassName = '{classDBName}';")
                self.commit()
            except:
                print(f"Sorry! No assignments of class {classDBName} exists in our database...")

            try: 
                self.query(f"DROP TABLE {self.name + classDBName};")
                self.commit()
            except:
                print(f"Sorry! No class {classDBName} exists in our database...")
        
        print("All done... Thanks!")

    def _calculateAssignmentAverage(self, classDB, classDBName, assignmentType):
        tableName = self.name + classDBName
        assignmentType = assignmentType.upper() # Double check during debugging

        self.query(f"SELECT COUNT(*)\
                     FROM Assignments\
                     WHERE ClassName = '{classDBName}' AND AssignmentType = '{assignmentType}';")
        amountOfAssignments = self.cur.fetchall()[0][0]

        classDB.query(f"SELECT DropAmount\
                        FROM {classDBName}\
                        WHERE AssignmentType = '{assignmentType}';")

        dropAmount = classDB.cur.fetchall()[0][0]
        keepAmount = amountOfAssignments - dropAmount if amountOfAssignments - dropAmount > 0 else amountOfAssignments
       
        self.query(f"SELECT Grade\
                     FROM Assignments\
                     WHERE AssignmentType = '{assignmentType}' AND ClassName = '{classDBName}'\
                     ORDER BY Grade DESC\
                     LIMIT {keepAmount};")
        temp = self.cur.fetchall()
        grades = []
        for grade in temp:
            grades.append(grade[0])
        avgGrade = round(sum(grades) / len(grades), 2)

        self.query(f"UPDATE {tableName}\
                     SET Grade = {avgGrade}\
                     WHERE AssignmentType = '{assignmentType}'")
        self.commit()