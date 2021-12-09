import database as db

class GradeBook(db.Database):
    def initDatabase(self):
        self.query("CREATE TABLE IF NOT EXISTS Students (uID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                         Name TEXT NOT NULL,\
                                                         CulmulativeGPA REAL DEFAULT 0);")

        self.query("CREATE TABLE IF NOT EXISTS Classes (cID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                        Name TEXT NOT NULL,\
                                                        Credits REAL DEFAULT 0)")

        self.commit()

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
                    FROM Classes;")
        return self.cur.fetchall()
    
    def printDB(self):
        print(f"Students:\n{self.getStudents()}\n")