from fastapi import FastAPI
from pydantic import BaseModel  # used for in-memory database
import sqlite3

cool_app = FastAPI()


def opening_db_connection(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    return cursor, conn


class User(BaseModel):
    name: str
    city: str


root_msg = {
    'success': True,
    'message': 'Custom Server Running'
}

sql_queries = {}

sql_queries['CreateUsersTable'] = """
    CREATE TABLE Users(
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    User_Name TEXT,
    User_City TEXT
    );
"""

sql_queries['DropUsersTable'] = """
    DROP TABLE IF EXISTS Users
"""

sql_queries['InsertUserRecord'] = """
    INSERT INTO Users (User_Name, User_City)
    VALUES 
        (?, ?)
"""

sql_queries['SelectAllfromUsers'] = """
    SELECT * FROM Users;
"""

data = [
    {
        'name': 'Irshad',
        'city': 'Karachi'
    },
    {
        'name': 'Ashfaq',
        'city': 'Lahore'
    },
    {
        'name': 'Waqar',
        'city': 'Islamabad'
    },
    {
        'name': 'Israr',
        'city': 'Multan'
    }
]


def show_all_users():
    cursor, conn = opening_db_connection('UsersDatabase.db')
    cursor.execute(sql_queries['SelectAllfromUsers'])
    x = cursor.fetchall()
    users_list = []
    for rec in x:
        ent_dict = {'id': rec[0], 'name': rec[1], 'city': rec[2]}
        users_list.append(ent_dict)
    conn.close()
    data_dict = {
        'success': True,
        'data': users_list
    }
    return data_dict


def show_user_by_id(id, msg, conn, cursor):
    query = f'SELECT * FROM Users WHERE User_ID = {id}'
    cursor.execute(query)
    val = cursor.fetchone()
    if val == None:
        conn.close()
        data_dict = {
            'success': False,
            'message': msg
        }
        return data_dict
    else:
        entry_dict = {'id': val[0], 'name': val[1], 'city': val[2]}
        conn.close()
        data_dict = {
            'success': True,
            'data': [entry_dict]
        }
        return data_dict


@cool_app.get('/')
def root():
    cursor, conn = opening_db_connection('UsersDatabase.db')
    cursor.execute(sql_queries['DropUsersTable'])
    cursor.execute(sql_queries['CreateUsersTable'])
    for i in data:
        cursor.execute(sql_queries['InsertUserRecord'], (i['name'], i['city']))
        conn.commit()
    conn.close()
    return root_msg


@cool_app.get('/api/users')
def get_all_users():
    data_dict = show_all_users()
    return data_dict


# @cool_app.get('/api/users/{id}')
@cool_app.get('/api/users/')
def get_user(user_id: int):
    cursor, conn = opening_db_connection('UsersDatabase.db')
    id = user_id
    data_dict = show_user_by_id(id=id, msg='Invalid ID - User does not exist', conn=conn, cursor=cursor)
    return data_dict


@cool_app.post('/api/users/')
def add_user(user: User):
    cursor, conn = opening_db_connection('UsersDatabase.db')
    cursor.execute(sql_queries['InsertUserRecord'], (user.name, user.city))
    conn.commit()
    data_dict = show_all_users()
    return data_dict


@cool_app.put('/api/users/')
def update_user(user: User, user_id: int):
    cursor, conn = opening_db_connection('UsersDatabase.db')
    id = user_id
    selection_query = f"""UPDATE Users SET User_Name = '{user.name}' , User_City = '{user.city}' WHERE User_ID = {id};"""
    resp = cursor.execute(selection_query)
    conn.commit()
    print(resp.rowcount)
    if resp.rowcount != 0:
        ent = {
            'id': id,
            'name': user.name,
            'city': user.city
        }
        conn.close()
        return {
            'success': True,
            'message': 'Record Updated',
            'data': [ent]
        }
    else:
        conn.close()
        return {
            'success': False,
            'message': 'Invalid ID - User does not exist'
        }


@cool_app.delete('/api/users/')
def delete_user(user_id: int):
    cursor, conn = opening_db_connection('UsersDatabase.db')
    query = f'SELECT * FROM Users WHERE User_ID = {user_id}'
    cursor.execute(query)
    val = cursor.fetchone()
    if val is None:
        conn.close()
        data_dict = {
            'success': False,
            'message': 'Invalid ID - User does not exist'
        }
        return data_dict
    else:
        entry_dict = {'id': val[0], 'name': val[1], 'city': val[2]}
        delete_query = f'DELETE FROM Users WHERE User_ID = {user_id};'
        cursor.execute(delete_query)
        conn.commit()
        conn.close()
        data_dict = {
            'success': True,
            'message': 'Mentioned below Record Deleted',
            'data': [entry_dict]
        }
        return data_dict
