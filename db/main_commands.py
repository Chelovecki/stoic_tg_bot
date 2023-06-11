import sqlite3
import os
from tools.json import read_from_json, write_in_json

if __name__ == '__main__':
    path_for_db = os.path.abspath('stoic_db.db')
    users_path_new_files = os.path.abspath('users_data')
    users_data = os.path.abspath('users_data')

else:
    path_for_db = os.path.join(os.path.abspath('db'), 'stoic_db.db')
    users_path_new_files = os.path.join(os.path.abspath('db'), 'user_scale.json')
    users_data = os.path.join(os.path.abspath('db'), 'users_data')




with sqlite3.connect(database=path_for_db) as connection:
    cursor = connection.cursor()

    def add_user_in_db(id_user):
        his_data = read_from_json(name_and_path=users_path_new_files)
        his_data['id_user'] = id_user
        write_in_json(name_and_path=f'{users_data}\\{id_user}.json', dictionary=his_data)
        query = f"""insert into user (id_user, file_path)
                values ('{id_user}', '{users_data}\\{id_user}.json')"""
        try:
            cursor.execute(query)
            connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_user_data(id_user):
        query = f"""select * from user"""
        cursor.execute(query)
        for row in cursor.fetchall():
            if row[0] == id_user:
                user_info = read_from_json(name_and_path=row[1])
                return user_info