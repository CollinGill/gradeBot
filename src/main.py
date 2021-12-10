#! python
import gradebook as gb
import classbook as cb
import student   as sb
import commands as cmd

# Central Databases
gradeBook = gb.GradeBook('GradeBook')
classBook = cb.ClassBook('ClassBook')

def main():
    # Students
    johnDoe          = cmd.createStudent(gradeBook, 'John Doe')
    janeDoe          = cmd.createStudent(gradeBook, 'Jane Doe')
    aliceWatson      = cmd.createStudent(gradeBook, 'Alice Watson')
    michaelHenderson = cmd.createStudent(gradeBook, 'Michael Henderson')