import sqlite3

class DB():
    def __init__(self, db_name):
        self.db_name = db_name
        self._create_all_tables()


    def _create_all_tables(self):
        self._create_table_books()
        self._create_table_users()

    def _create_table_books(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        q = ''' CREATE TABLE IF NOT EXISTS BOOKS (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            is_issued INTEGER DEFAULT 0,
            date_issued TEXT ,
            return_date TEXT
        )
        '''
        cursor.execute(q)

        conn.close()

    def _create_table_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        q = '''CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )'''
        cursor.execute(q)

        conn.close()

    def create_user(self,username, email, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        q = f'''
            INSERT INTO USERS (username,email,password) 
            VALUES ("{username}", "{email}", "{password}")
        '''
        cursor.execute(q)

        conn.commit()
        conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        q = "SELECT * FROM USERS"

        cursor.execute(q)
        print(cursor.fetchall())

        conn.close()

    def get_user_by_username(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        q = f'''
            SELECT * FROM USERS 
            WHERE username = "{username}"
        '''
        
        cursor.execute(q)
        result = cursor.fetchone()

        conn.close()

        if result is not None:
            d = {
                "id" : result[0],
                "username" : result[1],
                "email" : result[2],
                "password" : result[3],
                "is_admin" : result[4]
            }
            return d
        return result

    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        q = f'''
            SELECT * FROM USERS 
            WHERE email = "{email}"
        '''
        
        cursor.execute(q)
        result = cursor.fetchone()

        conn.close()

        if result is not None:
            d = {
                "id" : result[0],
                "username" : result[1],
                "email" : result[2],
                "password" : result[3],
                "is_admin" : result[4]
            }
            return d
        return result
