import sqlite3
import os
from os import path

if __name__ == '__main__':
    path_for_db = os.path.abspath('stoic_db.db')
else:
    path_for_db = os.path.join(os.path.abspath('db'), 'stoic_db.db')

connection = sqlite3.connect(database=path_for_db)
cursor = connection.cursor()
