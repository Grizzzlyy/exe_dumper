import json
import logging
import os

import magic
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from back import parse_elf
from back import parse_exe

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_file_type(file_path):
    mime = magic.Magic(mime=True)  # Возвращает MIME-тип файла
    file_type = mime.from_file(file_path)
    return file_type


# Функция для вставки данных о файле в базу
class BD_int():
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        self.cursor = self.conn.cursor()
        logging.basicConfig(
            filename='BD/file_processing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def __insert_file(self, username, file_type, header_first, header_second, import_table, export_table, file_name):
        self.cursor.execute('''
            INSERT INTO files (username, filetype, header_first, header_second, import_table, export_table, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING idx
        ''', (username, file_type, json.dumps(header_first), json.dumps(header_second), json.dumps(import_table),
              json.dumps(export_table), file_name))
        self.conn.commit()
        generated_id = self.cursor.fetchone()[0]
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
                                     file_type='elf',
                                     header_first=header,
                                     header_second=segments,
                                     import_table=sections,
                                     export_table=symbols,
                                     file_name=os.path.basename(file_path))
        return file_id

    def user_exists(self, username):
        self.cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        return self.cursor.fetchone() is not None

    def add_user(self, username, email, pwd_hash):
        try:
            if not self.user_exists(username):
                self.cursor.execute("""
                                    INSERT INTO users (username, is_admin, is_blocked, email, pwd_hash) 
                                    VALUES (%s, false, false, %s, %s)
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
            elif 'application' in file_type and 'exec' in file_type:
                file_id = self.__insert_elf(username, file_path)
            return file_id
        except Exception as e:
            logging.info(e)
            return -1

    def check_admin(self, admin):
        self.cursor.execute("SELECT is_admin FROM users WHERE username = %s", (admin,))
        return self.cursor.fetchone() == (True,)

    def get_user_name(self, email):
        try:
            self.cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            logging.info(f"[ERROR] {e}")
            return None

    def get_email(self, username):
        try:
            self.cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            logging.info(f"[ERROR] {e}")
            return None

    def change_user_access(self, username, ban):
        try:
            status = True if ban else False
            self.cursor.execute("UPDATE users SET is_blocked = %s WHERE username = %s", (status, username))
            self.conn.commit()
            if status:
                logging.info(f"[SUCCESS] user:{username} is blocked")
            else:
                logging.info(f"[SUCCESS] user:{username} is unblocked")
        except Exception as e:
            logging.info(f"[ERROR] {e}")

    def add_2f_code(self, username, code):
        try:
            self.cursor.execute("UPDATE users SET two_factor_code = %s WHERE username = %s", (code, username))
            logging.info(f"[SUCCESS] added code: {code} for user:{username}")
        except Exception as e:
            logging.info(f"[ERROR] {e}")

    def get_report(self, username, file_id):
        tmp_cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # Возвращать строки как словарь
        tmp_cursor.execute('SELECT * FROM files WHERE idx = %s AND username = %s', (file_id, username,))
        report = tmp_cursor.fetchone()

        if report is not None:
            report = dict(report)
            del report["username"]

        return report

    def get_user_info(self, username=None, email=None):
        try:
            if not username and not email:
                raise ValueError("Either 'username' or 'email' must be provided")

            condition = "email = %s" if email else "username = %s"
            param = email if email else username

            self.cursor.execute(
                f'SELECT username, email, is_admin, is_blocked, pwd_hash FROM users WHERE {condition}',
                (param,))
            report = self.cursor.fetchone()

            if report is None:
                return None

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
        self.cursor.execute("SELECT username, is_admin, is_blocked, email FROM users")
        users = self.cursor.fetchall()

        result = [
            {
                "username": user[0],
                "has_access": not user[2],
                "email": user[3]
            }
            for user in users
        ]
        return result

    def get_filename_by_idx(self, username, file_idx):
        self.cursor.execute("SELECT file_name, username FROM files WHERE idx = %s", (file_idx,))
        answer = self.cursor.fetchone()
        if not answer or username != answer[1]:
            return None
        return answer[0]

    def get_history(self, username):
        self.cursor.execute('SELECT idx, file_name FROM files WHERE username = %s', (username,))
        report = [{"file_id": row[0], "filename": row[1]} for row in self.cursor.fetchall()]
        return report

    def __del__(self):
        self.conn.close()
