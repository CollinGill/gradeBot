import os
import database as db

# This class connects to the ClassBook database
# This database contains a table for each class where it details the types of assignments along with the percent of grade and amount of grades you can drop of this that type
# There is also an accompanying table that holds the lower grade cutoff for different grades
class ClassBook(db.Database):
    #--Public Methods--#
    # Creates the class tables
    async def createClass(self, gradeDB, bot, author, className, credits):
        def check(message):
            return message.author == author

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
            await author.send(f"No class assignments or grade cutoffs have been registered at this for {classDBName}...")
            await author.send(f"NOTE... These are required unless you are immediately putting in a final grade for {classDBName}")
            await author.send("Would you like to continue? Yes to continue adding information, no to return to dialogue... (y/n)?")
            cont = await bot.wait_for('message', check=check)
            cont = cont.content.strip().lower()
            if cont == 'y':
                await self.initClass(className, bot, author)
            else:
                await author.send("All done... Thanks!")

    # Instantiates the class tables with the data pertaining to the class
    async def initClass(self, className, bot, author):
        def check(message):
            return message.author == author

        classDBName = ''.join(className.upper().split())
        classCutoffDB = classDBName + 'Cutoff'

        await author.send(f'\nPlease have the syllabus for {classDBName} available')
        await author.send("First up is assignment categories...")
        await author.send("How many types of assignments are there?")
        assignmentNums = await bot.wait_for('message', check=check)
        assignmentNums = int(assignmentNums.content)

        for i in range(assignmentNums):
            await author.send(f"\nAssignment type {i+1}:")
            await author.send("What is the type of assignment?")
            assignmentType = await bot.wait_for('message', check=check)
            assignmentType = assignmentType.content.upper()

            await author.send("What percent of the final grade is this type worth? ('50' for 50%)")
            percentOfGrade = await bot.wait_for('message', check=check)
            percentOfGrade = float(percentOfGrade.content) 

            await author.send("How many grades of this type can you drop?")
            dropAmount = await bot.wait_for('message', check=check)
            dropAmount = int(dropAmount.content)
            self.query(f"INSERT INTO {classDBName}(AssignmentType, PercentOfGrade, DropAmount) VALUES('{assignmentType}', {percentOfGrade}, {dropAmount});")

        await author.send("Now, grade cutoffs...")

        await author.send("What is the lower grade cutoff for an A?")
        A      = await bot.wait_for('message', check=check)
        A      = float(A.content)

        await author.send("What is the lower grade cutoff for an A-?")
        AMinus = await bot.wait_for('message', check=check)
        AMinus = float(AMinus.content)
        
        await author.send("What is the lower grade cutoff for an B+?")
        BPlus  = await bot.wait_for('message', check=check)
        BPlus  = float(BPlus.content)

        await author.send("What is the lower grade cutoff for an B?")
        B      = await bot.wait_for('message', check=check)
        B      = float(B.content)

        await author.send("What is the lower grade cutoff for an B-?")
        BMinus = await bot.wait_for('message', check=check)
        BMinus = float(BMinus.content)

        await author.send("What is the lower grade cutoff for an C+?")
        CPlus  = await bot.wait_for('message', check=check)
        CPlus  = float(CPlus.content)

        await author.send("What is the lower grade cutoff for an C?")
        C      = await bot.wait_for('message', check=check)
        C      = float(C.content)

        await author.send("What is the lower grade cutoff for an D?")
        D      = await bot.wait_for('message', check=check)
        D      = float(D.content)

        await author.send("What is the lower grade cutoff for an F?")
        F      = await bot.wait_for('message', check=check)
        F      = float(F.content)

        self.query(f"INSERT INTO {classCutoffDB}(A, AMinus, BPlus, B, BMinus, CPlus, C, D, F) VALUES({A},{AMinus},{BPlus},{B},{BMinus},{CPlus},{C},{D},{F});")
        
        self.commit()
        await author.send("All done... Thanks!")

    def updateGradeCutoff(self):
        className = input("What class would you like to change the grade cutoffs to? ").strip()
        classDBName = ''.join(className.upper().split())
        classCutoffDB = classDBName + 'Cutoff'

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
        self.query(f"UPDATE {classCutoffDB}\
                     SET A = {A},\
                         AMinus = {AMinus},\
                         BPlus  = {BPlus},\
                         B      = {B},\
                         BMinus = {BMinus}\
                         CPlus  = {CPlus},\
                         C      = {C},\
                         D      = {D},\
                         F      = {F};")
        
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

    async def printDB(self, author):
        await author.send(f"ClassBook:\n{self._classesList()}\n")

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
    async def _purgeClass(self, gradeDB, bot, author):
        def check(message):
            return message.author == author

        await author.send("What class would you like to purge?")
        className = await bot.wait_for('message', check=check)
        className = className.content
        classDBName = ''.join(className.upper().split())
        classCutoffDB = classDBName + 'Cutoff'

        await author.send(f"Are you sure you want to purge {classDBName}? (y/n)")
        confirmation = await bot.wait_for('message', check=check)
        confirmation = confirmation.content.strip().upper()

        if confirmation == "Y":
            try:
                self.query(f"DROP TABLE {classDBName};")
                self.query(f"DROP TABLE {classCutoffDB};")
                self.commit()
            except:
                await author.send(f"Sorry! No class {classDBName} exists in our database...")
                await author.send("Here are our current classes:")
                self.printDB(author)
            try:
                gradeDB.query(f"DELETE FROM ClassList WHERE Name = '{classDBName}';")
                gradeDB.commit()
            except:
                await author.send(f"Sorry! No class {classDBName} exists in our class database...")

        print("All done... Thanks!")

    def _classesList(self):
        classList = []
        for item in self.tables:
            if not item.endswith('Cutoff'):
                classList.append(item)
        return classList