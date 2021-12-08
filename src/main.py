#! python
import database as db

def main():
    database = db.Database('Students') # name is hardcoded now for testing purposes
    database.initDB()
    database.printDB()

if __name__ == '__main__':
    main()