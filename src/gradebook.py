import database as db

class GradeBook(db.Database):
    #--Public Methods--#
    def getStudents(self):
        self.query("SELECT *\
                    FROM Students;")
        studentNames = []
        students = self.cur.fetchall()
        for i in range(len(students)):
            studentNames.append(students[i][1])
        return studentNames

    def getClasses(self):
        self.query("SELECT Name, Credits\
                    FROM ClassList;")
        return self.cur.fetchall()
    
    def printDB(self):
        print(f"Students:\n{self.getStudents()}\n")

    #--Private Methods--#
    def _initDatabase(self):
        self.query("CREATE TABLE IF NOT EXISTS Students (uID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                         Name TEXT NOT NULL,\
                                                         CulmulativeGPA REAL DEFAULT 0);")

        # I believe this is unnecessary
        self.query("CREATE TABLE IF NOT EXISTS ClassList (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                          Name TEXT NOT NULL,\
                                                          Credits REAL DEFAULT 0)")

        self.commit()