import sqlite3
import bcrypt
def create_admin():
    conn = sqlite3.connect("project.db")
    cursor = conn.cursor()
    normal_pw = "admin_password"
    hashed_pw = bcrypt.hashpw(normal_pw.encode(), bcrypt.gensalt(10))
    string_hash_pw = hashed_pw.decode()
    print(string_hash_pw)
    cursor.execute(f"INSERT INTO USER(username, email, password, is_admin) VALUES('admin', 'admin@library.com','{string_hash_pw}',1)")
    conn.commit()

create_admin()
