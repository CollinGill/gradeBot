from dotenv import load_dotenv
import os
import discord
import logging
import gradebook as gb
import classbook as cb
import commands as cmd

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

gradeBook = gb.GradeBook('GradeBook')
classBook = cb.ClassBook('ClassBook')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_disconnect(self):
        print(f"Disconnected...")

    async def on_message(self, message):
        author = message.author
        content = message.content
        if author == self.user:
            return
        if not content.startswith('>'):
            return
        
        content = content[1:].strip()
        await self.messageHelper(author, content)

    async def messageHelper(self, author, content):
        def check(message):
            return message.author == author
        if content == 'bing':
            await author.send("bong \(^-^)/")
        elif content.lower() == 'hello':
            gradeBook.query(f"SELECT Name\
                              FROM Students\
                              WHERE DiscordName = '{author.id}'")
            name = gradeBook.cur.fetchone()
            if name == None:
                await author.send(f"{author}, what's your first and last name?")
                name = await self.wait_for('message', check=check)
                name = name.content.strip()
            else:
                name = name[0]
            currentStudent = cmd.createStudent(gradeBook, author.id, name)
            await author.send(f"Hello {currentStudent.name}!")
            while True:
                await author.send("What would you like to do?\n\
                                   1. Check overall GPA\n\
                                   2. Check the cumulative gpa for a semester\n\
                                   3. Check class grades for a semester\n\
                                   4. Check grades in a class\n\
                                   5. Add a class\n\
                                   6. Add an assignment to a class\n\
                                   7. Finalize a class's grade\n\
                                   8. Remove class from yourself")
                num = await self.wait_for('message', check=check)
                num = int(num.content.strip())
                if num == 1:
                    gpa = currentStudent.getCumulativeGpa(gradeBook)
                    await author.send(f"Your cumulative gpa is {gpa}")
                elif num == 2:
                    msg = []
                    semesters = currentStudent.getGpaList()
                    for semesterNum, gpa in semesters:
                        msg.append(f"Your gpa for semester {semesterNum} is {gpa}")
                    msg = '\n'.join(msg)
                    await author.send(msg)
                elif num == 3:
                    classes = await currentStudent.getSemesterGrades(self, author)
                    if type(classes) == str:
                        await author.send(classes)
                    else:
                        msg = []
                        for className, classGrade in classes:
                            msg.append(f'{className}: {classGrade}')
                        msg = '\n'.join(msg)
                        await author.send(msg)
                elif num == 4:
                    assignments = await currentStudent.getGrades(self, author)
                    if assignments:
                        msg = []
                        for assignmentType, grade in assignments:
                            msg.append(f"{assignmentType}: {grade}")
                        msg = '\n'.join(msg)
                        await author.send(msg)
                    else:
                        await author.send("No assignments in class")
                elif num == 5:
                    await currentStudent.addClass(gradeBook, classBook, self, author)
                elif num == 6:
                    await currentStudent.addGrade(classBook, self, author)
                elif num == 7:
                    await currentStudent.finalizeGrade(gradeBook, self, author)
                elif num == 8:
                    await currentStudent._deleteClass(self, author)

                #--Commands not meant for user access--#
                elif num == -1:
                    await classBook._purgeClass(gradeBook, self, author)
                elif num == -2:
                    await classBook.printDB(author)
                elif num == -3:
                    await author.send(str(gradeBook.getStudents()))
                
                await author.send("Would you like to continue? (y/n)")
                cont = await self.wait_for('message', check=check)
                cont = cont.content.strip().lower()
                if cont == 'n':
                    break
            await author.send("Thank you, bye! \\(^-^)/")
            currentStudent = None
        elif content.lower() == 'help':
            await author.send('Hello \(^-^)/\nPlease type `> hello` in order to access the dialogue options!')