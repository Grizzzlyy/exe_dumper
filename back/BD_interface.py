import sqlite3
import json
import logging
import os

import magic
from dotenv import load_dotenv

from back import parse_exe
from back import parse_elf
from back.parse_file import get_chunk

load_dotenv()

BD_path = os.getenv("DB_PATH")


def get_file_type(file_path):
    mime = magic.Magic(mime=True)  # Возвращает MIME-тип файла
    file_type = mime.from_file(file_path)
    return file_type


# Функция для вставки данных о файле в базу
class BD_int():
    def __init__(self):
        self.conn = sqlite3.connect(BD_path)
        self.cursor = self.conn.cursor()
        logging.basicConfig(
            filename='BD/file_processing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def __insert_file(self, username, file_type, header_first, header_second, import_table, export_table,file_name):
        self.cursor.execute('''
            INSERT INTO files (username, filetype, header_first, header_second, import_table, export_table, file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, file_type, json.dumps(header_first), json.dumps(header_second), json.dumps(import_table),
              json.dumps(export_table),file_name))
        self.conn.commit()
        generated_id = self.cursor.lastrowid
        logging.info(f"[SUCCESS] File with id:{generated_id} added")
        return generated_id

    def __insert_exe(self, username, file_path):
        parsed_ms_dos, parsed_pe_header, parsed_exports, parsed_imports = parse_exe.parse(file_path)
        file_id = self.__insert_file(username=username,
                                     file_type='exe',
                                     header_first=parsed_ms_dos,
                                     header_second=parsed_pe_header,
                                     import_table=parsed_imports,
                                     export_table=parsed_exports,
                                     file_name=os.path.basename(file_path))
        return file_id

    def __insert_elf(self, username, file_path):
        header, segments, sections, symbols = parse_elf.parse_elf_header(file_path)
        file_id = self.__insert_file(username=username,
                                     file_type='exe',
                                     header_first=header,
                                     header_second=segments,
                                     import_table=sections,
                                     export_table=symbols,
                                     file_name=os.path.basename(file_path))
        return file_id

    def user_exists(self, username):
        res = self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        res = res.fetchone()
        return res is not None

    def add_user(self, username, email, pwd_hash):
        try:
            if not self.user_exists(username):
                self.cursor.execute("""
                                    INSERT INTO users (username, is_admin, is_blocked, email, pwd_hash) 
                                    VALUES (?, 0, 0, ?, ?)
                                    """, (username, email, pwd_hash))
                self.conn.commit()
                logging.info(f"[SUCCESS] user {username} was added to users table")
            else:
                return "user_exists"
        except Exception as e:
            logging.info(e)

    def add_file(self, username, file_path):
        try:
            file_type = get_file_type(file_path)
            if 'exec' not in file_type:
                raise ValueError(f"incorrect filetype:{file_path} - type:{file_type}")

            if 'application' in file_type and ('portable-executable' in file_type or 'x-dosexec' in file_type):
                file_id = self.__insert_exe(username, file_path)
            elif file_type == 'application/x-executable':
                file_id = self.__insert_elf(file_path)
            return file_id
        except Exception as e:
            logging.info(e)
            return -1

    def check_admin(self, admin):
        res = self.cursor.execute("SELECT is_admin FROM users WHERE username = ?", (admin,))
        res = res.fetchone()
        return res == (1,)
    def get_user_name(self,email):
        try:
            username = self.cursor.execute("SELECT username FROM users WHERE email = ?",(email,)).fetchone()[0]
            return username
        except Exception as e:
            logging.info(f"[ERROR] {e}")
            return None
    def get_email(self,username):
        try:
            email = self.cursor.execute("SELECT email FROM users WHERE username = ?",(username,)).fetchone()[0]
            return email
        except Exception as e:
            logging.info(f"[ERROR] {e}")
            return None

    def change_user_access(self, username, ban):
        try:
            status = 1 if ban == True else 0
            self.cursor.execute("UPDATE users set is_blocked = {status} WHERE username = ?", (username,))
            self.conn.commit()
            logging.info(f"[SUCCESS] user:{username} is blocked")
        except Exception as e:
            logging.info(f"[ERROR] {e}")

    def add_2f_code(self, username, code):
        try:
            self.cursor.execute("UPDATE users set two_factor_code = ? WHERE username = ?", (code, username))
            logging.info(f"[SUCCESS] added code: {code} for user:{username}")
        except Exception as e:
            logging.info(f"[ERROR] {e}")

    # TODO use self.conn etc, like you want
    def get_report(self, file_id):
        self.conn.row_factory = sqlite3.Row  # gets strings as a dict
        self.cursor = self.conn.cursor()
        report = self.cursor.execute(f'SELECT * FROM files WHERE idx = {file_id}').fetchone()

        self.conn.close()

        if report is not None:
            report = dict(report)
            del report["username"]
            json_fields = ["header_first", "header_second", "import_table", "export_table"]
            for k in json_fields:
                report[k] = json.loads(report[k])

        return report
    def get_user_info(self, username=None, email=None):
        try:
            if not username and not email:
                raise ValueError("Either 'username' or 'email' must be provided")

            condition = "email = ?" if email else "username = ?"
            param = email if email else username

            report = self.cursor.execute(f'SELECT username, email, is_admin, is_blocked, pwd_hash FROM users WHERE {condition}', (param,)).fetchone()

            if report is None:
                return None  # Можно также выбросить исключение или вернуть ошибку

            user_info = {
                'username': report[0],
                'email': report[1],
                'is_admin': bool(report[2]),
                'has_access': not bool(report[3]),
                'pwd_hash': report[4]
            }

            return user_info
        except Exception as e:
            logging.info(f"[ERROR]: e")
            return e
    def get_list_of_users(self):
        query = "SELECT username, is_admin, is_blocked, email FROM users"
        users = self.cursor.execute(query).fetchall()

        # Преобразование результата в список словарей
        result = [
            {
                "username": user[0],
                "has_access": not user[2],  # Обратное значение is_blocked
                "email": user[3]
            }
            for user in users
        ]
        return result

    
    def get_history(self,username):
        answer = self.cursor.execute(f'SELECT idx, file_name from files WHERE username = ?',(username,)).fetchall()
        report = [{"file_id": row[0], "filename": row[1]} for row in answer]
        return report
        
    def __del__(self):
        print("deleted")
        self.conn.close()


if __name__ == "__main__":
    bd = BD_int()
    report = bd.add_file("milniy", "./files/HxD.exe")
    pass
