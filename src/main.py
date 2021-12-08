#! python
import database as db

def main():
    gradeBook = db.GradeBook('gradeBook')
    db.createStudent(gradeBook, 'John Doe')
    db.createStudent(gradeBook, 'Jane Doe')
    gradeBook.printDB()

if __name__ == '__main__':
    main()