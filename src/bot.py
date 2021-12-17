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
        if content == 'bing':
            await author.send("bong \(^-^)/")
        elif content.lower() == 'hello':
            gradeBook.query(f"SELECT Name\
                              FROM Students\
                              WHERE DiscordName = '{author}'")
            name = gradeBook.cur.fetchone()
            if name == None:
                await author.send(f"{author}, what's your first and last name?")
                name = await self.wait_for('message')
                name = name.content.strip()
            else:
                name = name[0]
            currentStudent = cmd.createStudent(gradeBook, author, name)
            await author.send(f"Hello {currentStudent.name}!")
            await author.send("What would you like to do?\n\
                               1. Check overall GPA\n\
                               2. Check class grades for a semester\n\
                               3. Check grades in a class\n\
                               4. Add a class\n\
                               5. Add an assignment to a class\n\
                               6. Finalize a class's grade")
            num = await self.wait_for('message')
            num = int(num.content.strip())