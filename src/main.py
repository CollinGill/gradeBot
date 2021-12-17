#! python
import bot
import gradebook as gb
import classbook as cb
import commands as cmd

gradeBook = gb.GradeBook('GradeBook')
classBook = cb.ClassBook('ClassBook')

def discordRun():
    client = bot.MyClient()
    client.run(bot.TOKEN)

if __name__ == '__main__':
    yn = input("Do you want to start the discord bot? (y/n) ").strip().lower()
    if yn == 'y':
        discordRun()