import student   as sb
from pprint import pprint

def createStudent(gradeBookDB, name):
    studentDBName = name.split()[0].lower() + name.split()[1]
    if name in gradeBookDB.getStudents():
        print('NOTE: Name already in database...')
        return sb.StudentDB(studentDBName)
    gradeBookDB.query(f"INSERT INTO Students(Name) VALUES('{name}')")
    gradeBookDB.commit()
    return sb.StudentDB(studentDBName)

def createClass(gradeDB, studentDB, classDB, className, credits, semesterNum):
    classDBName = ''.join(className.upper().split())
    tableName = studentDB.name + classDBName
    
    gradeDB.query(f"INSERT INTO Classes(Name, Credits) VALUES('{classDBName}', {credits});")
    gradeDB.commit()

    classDB.query(f"CREATE TABLE IF NOT EXISTS {classDBName} (aID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                              AssignmentType TEXT NOT NULL,\
                                                              PercentOfGrade REAL NOT NULL DEFAULT 0,\
                                                              DropAmount INTEGER NOT NULL DEFAULT 0);")
    if classDB.getClass(classDBName) == []:
        initClass(classDB, className)
    else:
        print('NOTE: Class already in database...')
    classDB.commit()

    studentDB.query(f"CREATE TABLE IF NOT EXISTS {tableName} (aID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                              AssignmentType TEXT NOT NULL,\
                                                              AssignmentName TEXT NOT NULL,\
                                                              Grade REAL NOT NULL DEFAULT 0);")
    studentDB.query(f"INSERT INTO Semester(SemesterNum, Name, Credits) VALUES({semesterNum}, '{classDBName}', {credits});")
    studentDB.commit()

def initClass(classDB, className):
    classDBName = ''.join(className.upper().split())
    print(f'\nPlease have the syllabus for {classDBName} available')
    assignmentNums = int(input("How many types of assignments are there? "))
    for i in range(assignmentNums):
        print(f"\nAssignment type {i+1}:")
        assignmentType = input("What is the type of assignment? ").upper()
        percentOfGrade = float(input("What is the percent of the final grade is this type worth? (Enter like '50') "))
        dropAmount     = int(input("How many grades of this type can you drop? "))
        classDB.query(f"INSERT INTO {classDBName}(AssignmentType, PercentOfGrade, DropAmount) VALUES('{assignmentType}', {percentOfGrade}, {dropAmount})")
    
    print("All done... Thanks!")

def getClassStats(classDB, className):
    classDBName = ''.join(className.upper().split())
    classDB.query(f"SELECT *\
                    FROM {classDBName};")
    return classDB.cur.fetchall()

def calculateAssignmentAverage(studentDB, className, assignmentType):
    classDBName = ''.join(className.upper().split())
    tableName = studentDB.name + classDBName

    studentDB.query(f"SELECT ROUND(AVG(Grade), 4)\
                      FROM {tableName}\
                      WHERE AssignmentType = '{assignmentType}';")