import sqlite3
import json
import logging
import os

import magic
from dotenv import load_dotenv

from back import parse_exe
from back import parse_elf
from back.parse_file import file_to_hex

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

    def __insert_file(self, username, file_type, header_first, header_second, import_table, export_table):
        self.cursor.execute('''
            INSERT INTO files (username, filetype, header_first, header_second, import_table, export_table)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, file_type, json.dumps(header_first), json.dumps(header_second), json.dumps(import_table),
              json.dumps(export_table)))
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
                                     export_table=parsed_exports)
        return file_id

    def __insert_elf(self, username, file_path):
        header, segments, sections, symbols = parse_elf.parse_elf_header(file_path)
        file_id = self.__insert_file(username=username,
                                     file_type='exe',
                                     header_first=header,
                                     header_second=segments,
                                     import_table=sections,
                                     export_table=symbols)
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

    def ban_user(self, admin, username):
        try:
            if not self.check_admin(admin):
                raise ValueError(f"Not an admin:{admin} try to ban user:{username}")
            if self.check_admin(username):
                raise ValueError(f"Try to ban admin:{username}")
            self.cursor.execute("UPDATE users set is_blocked = 1 WHERE username = ?", (username,))
            self.conn.commit()
            logging.info(f"[SUCCESS] user:{username} is blocked")
        except Exception as e:
            logging.info(f"[ERROR] {e}")
    def add_2f_code(self,username,code):
        try: 
            self.cursor.execute("UPDATE users set two_factor_code = ? WHERE username = ?", (code,username))
            logging.info(f"[SUCCESS] added code: {code} for user:{username}")
        except Exception as e:
            logging.info(f"[ERROR] {e}")


    # TODO use self.conn etc, like you want
    def get_report(self, file_id):
        self.conn.row_factory = sqlite3.Row  # gets strings as a dict
        self.cursor = self.conn.cursor()
        subd_answer = self.cursor.execute(f'SELECT * FROM files WHERE idx = {file_id}').fetchone()
        
        self.conn.close()
        report = dict()
        if subd_answer is not None:
            subd_answer = dict(subd_answer)
            if subd_answer['filetype'] == 'exe':
                report['MS_DOS_header'] = json.loads(subd_answer['header_first'])
                report['PE_header'] = json.loads(subd_answer['header_second'])
                report['Import_table'] = json.loads(subd_answer['import_table'])
                report['Export_table'] = json.loads(subd_answer['export_table'])
            else:
                json_fields = [ 'header', 'segments', 'sections', 'symbols']
                report['ELF_header'] = json.loads(subd_answer['header_first'])
                report['Segments'] = json.loads(subd_answer['header_second'])
                report['Sections'] = json.loads(subd_answer['import_table'])
                report['Symbols'] = json.loads(subd_answer['export_table'])

            file_name = subd_answer['file_name']
            file_content = file_to_hex(file_path='files/'+file_name)
            report["file_content"] = file_content
        return subd_answer



    def __del__(self):
        self.conn.close()


# Testing
if __name__ == "__main__":
    bd = BD_int()
    report = bd.get_report(2)
    pass
