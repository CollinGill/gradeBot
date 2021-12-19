import os
import database as db
import commands as cmd
import sqlite3
from pprint import pprint

from gradebook import GradeBook

# This class connects to the ClassBook database
# This database several tables of data pertain only to the individual student: SemesterGpas, Assignments, Grades in a class
class StudentDB(db.Database):
    #--Public Methods--#
    def __init__(self, discordName, name):
        self.name = name
        self.discordName = discordName
        self._dbLocation = self._createDBFile(self.name) # unsure if needed
        self.con = sqlite3.connect(self._dbLocation)
        self.cur = self.con.cursor()
        self.tables = []
        self._initDatabase()
    
    def getCumulativeGpa(self, gradeDB):
        gradeDB.query(f"SELECT CumulativeGPA FROM Students WHERE DiscordName = '{self.discordName}';")
        return gradeDB.cur.fetchone()[0]

    def getGpaList(self):
        self.query("SELECT *\
                    FROM SemesterGpa;")
        return self.cur.fetchall()
    
    async def getSemesterGrades(self, bot, author):
        def check(message):
            return message.author == author
        await author.send("What semester would you like to check?")
        semesterNum = await bot.wait_for('message', check=check)
        semesterNum = int(semesterNum.content)
        self.query(f"SELECT ClassName, CurrentGrade\
                     FROM ClassGrades\
                     WHERE SemesterNum = {semesterNum}\
                     ORDER BY ClassName;")
        semesterList = self.cur.fetchall()
        return semesterList if semesterList != [] else f'No grades for semester {semesterNum}...'

    async def getGrades(self, bot, author):
        def check(message):
            return message.author == author
        await author.send("What class would you like a report of?")
        className = await bot.wait_for('message', check=check)
        className = className.content
        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName

        self.query(f"SELECT AssignmentType, Grade\
                     FROM {tableName}\
                     WHERE Grade != -1;")
        return self.cur.fetchall()

    async def addClass(self, gradeDB, classDB, bot, author):
        def check(message):
            return message.author == author
        await author.send("What class would  you like to add? (Please use the class code, ex. 'MATH 250') (type `cancel` to cancel)")
        className = await bot.wait_for('message', check=check)
        className = className.content

        if className.lower().strip() == 'cancel':
            return

        classDBName = ''.join(className.upper().split())
        tableName = self.name + classDBName
        await author.send("How many credits do you get from this class?")
        credits = await bot.wait_for('message', check=check)
        credits = float(credits.content)
        await author.send("During which semester did you take this class? (i.e. 1, 2, 3, 4, etc.)")
        semesterNum = await bot.wait_for('message', check=check)
        semesterNum = int(semesterNum.content)

        self.query(f"CREATE TABLE IF NOT EXISTS {tableName} (aID            INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             AssignmentType TEXT NOT NULL,\
                                                             PercentOfGrade INTEGER NOT NULL DEFAULT 0,\
                                                             Grade          FLOAT NOT NULL DEFAULT -1);")
        self.query(f"INSERT INTO ClassGrades(SemesterNum, ClassName, Credits) VALUES({semesterNum}, '{classDBName}', {credits});")

        try:
            self.query(f"INSERT INTO SemesterGpa(SemesterNum, Gpa) VALUES({semesterNum}, -1)")
        except:
            # Pass since it means that the semester is already initialized
            pass

        self.commit()

        await classDB.createClass(gradeDB, bot, author, className, credits)
        
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

    async def addGrade(self, classDB, bot, author):
        def check(message):
            return message.author == author
        await author.send('What class would you like to add a grade to?')
        className   = await bot.wait_for('message', check=check)
        className   = className.content
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

        if tableName not in self.tables:
            await author.send(f"Sorry, {classDBName} not in your class list...")
            return

        await author.send("Current Class Assignments:")
        classStats = []
        temp = cmd.getClassStats(classDB, className)
        for assignment in temp:
            classStats.append(assignment[1])
        
        await author.send('\n'.join(classStats))

        await author.send("\nGrade Information:")

        await author.send("What is the name of the assignment?")
        assignmentName = await bot.wait_for('message', check=check)
        assignmentName = assignmentName.content.strip()

        await author.send("What is the type of the assignment?")
        assignmentType = await bot.wait_for('message', check=check)
        assignmentType = assignmentType.content.strip().upper()

        await author.send("What is the grade of the assignment?")
        grade = await bot.wait_for('message', check=check)
        grade = float(grade.content)

        if assignmentType not in classStats:
            await author.send(f"Sorry, {assignmentType} not in {classDBName}...")
            return

        self.query(f"INSERT INTO Assignments (ClassName, AssignmentType, AssignmentName, Grade) VALUES('{classDBName}',\
                                                                                                       '{assignmentType}',\
                                                                                                       '{assignmentName}',\
                                                                                                       {grade});")
        self.commit()

        self._calculateAssignmentAverage(classDB, classDBName, assignmentType)
        self._calculateClassGrade(classDB, classDBName)

        await author.send("All done... Thanks!")

    def removeAssignment(self, classDB):
        className   = input('What class would you like to delete from? ')
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

        if tableName not in self.tables:
            print(f"ERROR: {classDBName} not in {self.name}'s class list...")
            return

        print("Here's a list of grades...")
        self.query(f"SELECT AssignmentType, AssignmentName, Grade\
                     FROM Assignments\
                     WHERE ClassName = '{classDBName}';")
        pprint(self.cur.fetchall())

        assignmentName = input("What's the name of the assignment you would like to remove? (Case sensitive) ")
        self.query(f"SELECT AssignmentType\
                     FROM Assignments\
                     WHERE AssignmentName = '{assignmentName}' AND ClassName = '{classDBName}';")
        assignmentType = self.cur.fetchall()[0][0]
        self.query(f"DELETE\
                     FROM Assignments\
                     WHERE AssignmentName = '{assignmentName}' AND ClassName = '{classDBName}';")
        self.commit()
        self._calculateAssignmentAverage(classDB, classDBName, assignmentType)
        self._calculateClassGrade(classDB, classDBName)
        print("All done... Thanks!")

    def updateAssignment(self):
        pass

    async def finalizeGrade(self, gradeDB, bot, author):
        def check(message):
            return message.author == author

        await author.send("WARNING: Only use this once the grade has been finalized...")
        await author.send("Do you want to continue (y/n)")
        yn = await bot.wait_for('message', check=check)
        yn = yn.content.strip().lower()
        if yn != 'y':
            await author.send("All done... Thanks!")
            return

        await author.send("What class would you like to finalize?")
        className   = await bot.wait_for('message', check=check) 
        className   = className.content
        classDBName = ''.join(className.upper().split())
        tableName   = self.name + classDBName

        await author.send(f"What was your final grade in {classDBName}? (A, A-, B+, etc.)")
        grade = await bot.wait_for('message', check=check)
        grade = ''.join(grade.content.strip().upper().split())
        grade = self._getGradeFromLetter(grade)

        self.query(f"SELECT SemesterNum\
                     FROM ClassGrades\
                     WHERE ClassName = '{classDBName}';")
        semesterNum = self.cur.fetchall()[0][0]

        self.query(f"UPDATE ClassGrades\
                     SET CurrentGrade = {grade}, FinalGrade = {grade}\
                     WHERE ClassName = '{classDBName}';")
        self.query(f"DELETE FROM Assignments\
                     WHERE ClassName = '{classDBName}';")
        self.query(f"DROP TABLE IF EXISTS {tableName}")
        self.commit()

        self._calculateSemesterGPA(semesterNum)
        self._calculateCumulativeGPA(gradeDB)

        await author.send("All done... Thanks!")

    async def deleteClass(self, bot, author):
        def check(message):
            return message.author == author
        
        self.query("SELECT ClassName\
                    FROM ClassGrades\
                    ORDER BY ClassName;")
        output = self.cur.fetchall()
        classes = []

        i = 0
        for className in output:
            if i % 3 == 0 and i != 0:
                classes.append(f'{className[0]}\n\n')
            else:
                classes.append(f'{className[0]}\t')
            i += 1

        classes.append('\n')
        classes = ''.join(classes)

        await author.send(f"Here is a list of your classes:\n{classes}")
        await author.send("What class would you like to purge? (type `cancel` to cancel)")
        className = await bot.wait_for('message', check=check)
        className = className.content
        classDBName = ''.join(className.upper().split())

        if className.lower() == 'cancel':
            await author.send("All done... Thanks!")
            return

        await author.send(f"Are you sure you want to purge {classDBName}? (y/n)")
        confirmation = await bot.wait_for('message', check=check)
        confirmation = confirmation.content.strip().upper()

        if confirmation == "Y":
            try:
                self.query(f"DELETE\
                             FROM Assignments\
                             WHERE ClassName = '{classDBName}';")
                self.query(f"DELETE\
                             FROM ClassGrades\
                             WHERE ClassName = '{classDBName}';")
                self.commit()
            except:
                await author.send(f"Sorry! No assignments of class {classDBName} exists in your database...")

            try: 
                self.query(f"DROP TABLE {self.name + classDBName};")
                self.commit()
            except:
                await author.send(f"Sorry! No class {classDBName} exists in our database...")
        
        await author.send("All done... Thanks!")

    def printDB(self):
        print(f"{self.name}:\n{self.tables}\n")

    #--Private Methods--#
    def _initDatabase(self):
        self.query(f"CREATE TABLE IF NOT EXISTS SemesterGpa (SemesterNum INTEGER PRIMARY KEY,\
                                                             Gpa REAL NOT NULL DEFAULT 0);")
        
        self.query(f"CREATE TABLE IF NOT EXISTS ClassGrades (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                             SemesterNum INTEGER NOT NULL,\
                                                             ClassName TEXT NOT NULL,\
                                                             Credits REAL NOT NULL DEFAULT 0,\
                                                             CurrentGrade REAL NOT NULL DEFAULT -1,\
                                                             FinalGrade REAL NOT NULL DEFAULT -1,\
                                                             UNIQUE(ClassName));")

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
        avgGrade = round(sum(grades) / len(grades), 2) if len(grades) != 0 else -1

        self.query(f"UPDATE {tableName}\
                     SET Grade = {avgGrade}\
                     WHERE AssignmentType = '{assignmentType}'")
        self.commit()

    def _calculateClassGrade(self, classDB, classDBName):
        tableName = self.name + classDBName
        self.query(f"SELECT PercentOfGrade, Grade\
                     FROM {tableName};")
        assignmentGrades = self.cur.fetchall()
        totalPercentage = 0
        finalGrade = 0
        for percentOfGrade, grade in assignmentGrades:
            if grade != -1:
                finalGrade += grade * percentOfGrade / 100
                totalPercentage += percentOfGrade / 100

        currentGrade = round(finalGrade / totalPercentage, 4)

        currentGrade = self._getGradeFromPercent(classDB, classDBName, currentGrade)

        self.query(f"UPDATE ClassGrades\
                     Set CurrentGrade = {currentGrade}\
                     Where ClassName = '{classDBName}'")
        self.commit()
        

        if totalPercentage == 1:
            self.query(f"SELECT SemesterNum\
                         FROM ClassGrades\
                         WHERE ClassName = '{classDBName}';")
            semesterNum = self.cur.fetchall()[0][0]
            self._calculateSemesterGPA(semesterNum)

    def _calculateSemesterGPA(self, semesterNum):
        self.query(f"SELECT Credits, FinalGrade\
                     FROM ClassGrades\
                     WHERE SemesterNum = {semesterNum};")
        classGrades = self.cur.fetchall()
        totalCredits = 0
        rawGrade = 0
        for credits, grade in classGrades:
            if grade != -1:
                totalCredits += credits
                rawGrade += grade * credits
        
        semesterGrade = round(rawGrade / totalCredits, 4)
        self.query(f"UPDATE SemesterGpa\
                     SET Gpa = {semesterGrade}\
                     WHERE SemesterNum = {semesterNum};")
        self.commit()

    def _calculateCumulativeGPA(self, gradeDB):
        semesters = self.getGpaList()
        numSemesters = 0
        rawGpa = 0
        for _, gpa in semesters:
            numSemesters += 1
            rawGpa += gpa

        cumulativeGPA = round(rawGpa / numSemesters, 4)
        gradeDB.query(f"UPDATE Students\
                        SET CumulativeGPA = {cumulativeGPA}\
                        WHERE DiscordName = '{self.discordName}';")
        gradeDB.commit()
            

    def _getGradeFromPercent(self, classDB, classDBName, grade):
        gradeDict = {0: 0.00, 1: 1.00, 2: 2.00, 3: 2.33, 4: 2.67, 5: 3.00, 6: 3.33, 7: 3.67, 8: 4.00}
        classCutoff = classDBName + 'Cutoff'
        classDB.query(f"SELECT A, AMinus, BPlus, B, BMinus, CPlus, C, D, F\
                        FROM {classCutoff};")
        rawCutoff = classDB.cur.fetchall()[0]
        cutOffs = []
        for cutOff in rawCutoff:
            cutOffs.append(cutOff)

        cutOffs.reverse()
        cutOffIndex = len(cutOffs) - 1
        for i in range(len(cutOffs)):
            if grade < cutOffs[i]:
                cutOffIndex = i - 1 if i > 0 else 0
                break

        return gradeDict[cutOffIndex]

    def _getGradeFromLetter(self, grade):
        gradeDict = {'F': 0.00, 'D': 1.00, 'C': 2.00, 'C+': 2.33, 'B-': 2.67, 'B': 3.00, 'B+': 3.33, 'A-': 3.67, 'A': 4.00}
        return gradeDict[grade]