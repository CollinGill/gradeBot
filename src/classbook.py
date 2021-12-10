import os
import database as db

class ClassBook(db.Database):
    #--Public Methods--#
    def initClass(self, className):
        classDBName = ''.join(className.upper().split())
        print(f'\nPlease have the syllabus for {classDBName} available')
        assignmentNums = int(input("How many types of assignments are there? "))
        for i in range(assignmentNums):
            print(f"\nAssignment type {i+1}:")
            assignmentType = input("What is the type of assignment? ").upper()
            percentOfGrade = float(input("What is the percent of the final grade is this type worth? (Enter like '50') ")) 
            dropAmount     = int(input("How many grades of this type can you drop? "))
            self.query(f"INSERT INTO {classDBName}(AssignmentType, PercentOfGrade, DropAmount) VALUES('{assignmentType}', {percentOfGrade}, {dropAmount})")

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