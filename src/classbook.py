import os
import database as db

class ClassBook(db.Database):
    #--Public Methods--#
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
            studentDB.query(f"INSERT INTO {studentDB.name + classDBName}(AssignmentType, PercentOfGrade) VALUES('{assignmentType}', {percentOfGrade});")
        studentDB.commit()

        print("Now, grade cutoffs...")
        A      = float(input("What is the lower grade cutoff for an A? "))
        AMinus = float(input("What is the lower grade cutoff for an A-? "))
        BPlus  = float(input("What is the lower grade cutoff for an B+? "))
        B      = float(input("What is the lower grade cutoff for an B? "))
        BMinus = float(input("What is the lower grade cutoff for an B-? "))
        CPlus  = float(input("What is the lower grade cutoff for an C+? "))
        C      = float(input("What is the lower grade cutoff for an C? "))
        D      = float(input("What is the lower grade cutoff for an D? "))
        F      = float(input("What is the lower grade cutoff for an F? "))
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

    def _classesList(self):
        return self.tables