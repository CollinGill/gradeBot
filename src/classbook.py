import os
import database as db

# This class connects to the ClassBook database
# This database contains a table for each class where it details the types of assignments along with the percent of grade and amount of grades you can drop of this that type
# There is also an accompanying table that holds the lower grade cutoff for different grades
class ClassBook(db.Database):
    #--Public Methods--#
    # Creates the class tables
    def createClass(self, gradeDB, className=None, credits=None, semesterNum=None):
        if className == None or credits == None or semesterNum == None:
            className = input("What class would  you like to add? (Please use the class code, ex. 'MATH 250') ")
            credits = float(input("How many credits do you get from this class? "))
            semesterNum = int(input("During which semester are you taking this class? "))

        classDBName = ''.join(className.upper().split())
        classCutoff = classDBName + 'Cutoff'

        self.query(f"CREATE TABLE IF NOT EXISTS {classDBName} (aID            INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                               AssignmentType TEXT NOT NULL,\
                                                               PercentOfGrade REAL NOT NULL DEFAULT 0,\
                                                               DropAmount     INTEGER NOT NULL DEFAULT 0);")
        self.commit()

        self.query(f"CREATE TABLE IF NOT EXISTS {classCutoff} (gcID   INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                               A      REAL NOT NULL DEFAULT 0,\
                                                               AMinus REAL NOT NULL DEFAULT 0,\
                                                               BPlus  REAL NOT NULL DEFAULT 0,\
                                                               B      REAL NOT NULL DEFAULT 0,\
                                                               BMinus REAL NOT NULL DEFAULT 0,\
                                                               CPlus  REAL NOT NULL DEFAULT 0,\
                                                               C      REAL NOT NULL DEFAULT 0,\
                                                               D      REAL NOT NULL DEFAULT 0,\
                                                               F      REAL NOT NULL DEFAULT 0);")

        self.commit()

        if (classDBName, credits) in gradeDB.getClasses():
            print(f'NOTE: Class already in database...')
        else:
            gradeDB.query(f"INSERT INTO ClassList(Name, Credits) VALUES('{classDBName}', {credits});")
            gradeDB.commit()
            self.initClass(self, className)

    # Instantiates the class tables with the data pertaining to the class
    def initClass(self, studentDB, className):
        classDBName = ''.join(className.upper().split())
        classCutoffDB = classDBName + 'Cutoff'

        print(f'\nPlease have the syllabus for {classDBName} available')
        print("First up is assignment categories...")
        assignmentNums = int(input("How many types of assignments are there? "))
        for i in range(assignmentNums):
            print(f"\nAssignment type {i+1}:")
            assignmentType = input("What is the type of assignment? ").upper()
            percentOfGrade = float(input("What is the percent of the final grade is this type worth? (Enter like '50') ")) 
            dropAmount     = int(input("How many grades of this type can you drop? "))
            self.query(f"INSERT INTO {classDBName}(AssignmentType, PercentOfGrade, DropAmount) VALUES('{assignmentType}', {percentOfGrade}, {dropAmount});")
        studentDB.commit()

        print("Now, grade cutoffs...")
        A      = float(input("What is the lower grade cutoff for an A?  "))
        AMinus = float(input("What is the lower grade cutoff for an A-? "))
        BPlus  = float(input("What is the lower grade cutoff for an B+? "))
        B      = float(input("What is the lower grade cutoff for an B?  "))
        BMinus = float(input("What is the lower grade cutoff for an B-? "))
        CPlus  = float(input("What is the lower grade cutoff for an C+? "))
        C      = float(input("What is the lower grade cutoff for an C?  "))
        D      = float(input("What is the lower grade cutoff for an D?  "))
        F      = float(input("What is the lower grade cutoff for an F?  "))
        self.query(f"INSERT INTO {classCutoffDB}(A, AMinus, BPlus, B, BMinus, CPlus, C, D, F) VALUES({A},{AMinus},{BPlus},{B},{BMinus},{CPlus},{C},{D},{F});")
        
        self.commit()
        print("All done... Thanks!")

    def getClass(self, className):
        try:
            className = ''.join(className.upper().split())
            self.query(f"SELECT AssignmentType, PercentOfGrade, DropAmount\
                         FROM {className};")
            return self.cur.fetchall()
        except:
            return []

    def printDB(self):
        print(f"ClassBook:\n{self._classesList()}\n")

    #--Private Methods--#
    def _initDatabase(self):
        self._updateTables()
    
    def _createDBFile(self, name):
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

    # Purges all records of the class from the ClassBook and GradeBook
    def _purgeClass(self, gradeDB):
        className = input("What class would you like to purge? ")
        classDBName = ''.join(className.upper().split())
        classCutoffDB = classDBName + 'Cutoff'
        confirmation = input(f"Are you sure you want to purge {classDBName}? (y/n) ").upper()

        if confirmation == "Y":
            try:
                self.query(f"DROP TABLE {classDBName};")
                self.query(f"DROP TABLE {classCutoffDB};")
                self.commit()
            except:
                print(f"Sorry! No class {classDBName} exists in our database...")
                print("Here are our current classes:")
                self.printDB()
            try:
                gradeDB.query(f"DELETE FROM ClassList WHERE Name = '{classDBName}';")
                gradeDB.commit()
            except:
                print(f"Sorry! No class {classDBName} exists in our class database...")

        print("All done... Thanks!")

    def _classesList(self):
        classList = []
        for item in self.tables:
            if not item.endswith('Cutoff'):
                classList.append(item)
        return classList