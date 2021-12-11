import student as sb

# Creates a student object
def createStudent(gradeBookDB, name):
    studentDBName = name.split()[0].lower() + ''.join(name.split()[1:]) if ' ' in name else name.lower()
    if name in gradeBookDB.getStudents():
        print('NOTE: Name already in database...')
        return sb.StudentDB(studentDBName)
    gradeBookDB.query(f"INSERT INTO Students(Name) VALUES('{name}')")
    gradeBookDB.commit()
    return sb.StudentDB(studentDBName)

# Returns a list of assignment types for a specific class
def getClassStats(classDB, className):
    classDBName = ''.join(className.upper().split())
    classDB.query(f"SELECT *\
                    FROM {classDBName};")
    return classDB.cur.fetchall()
