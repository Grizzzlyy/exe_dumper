import sqlite3
import json
import magic
import logging
import parse_exe
import parse_elf

BD_path = 'BD/files.db'

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


    def __insert_file(cursor, conn, file_type, header_first, header_second, import_table, export_table):
        cursor.execute('''
            INSERT INTO files (file_type, header_first, header_second, import_table, export_table)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_type, json.dumps(header_first),json.dumps(header_second), json.dumps(import_table), json.dumps(export_table)))
        conn.commit()
        generated_id = cursor.lastrowid
        logging.info(f"File with id:{generated_id} added")
        return generated_id

    def __insert_exe(cursor, conn, file_path):
        parsed_ms_dos, parsed_pe_header, parsed_exports, parsed_imports = parse_exe.parse(file_path)
        file_id = BD_int.__insert_file(cursor, conn, 'exe',
                            header_first=parsed_ms_dos,
                            header_second=parsed_pe_header,
                            import_table=parsed_imports,
                            export_table=parsed_exports)
        return file_id

    def __insert_elf(cursor, conn, file_path):
        header,segments,sections,symbols = parse_elf.parse_elf_header(file_path)
        file_id = BD_int.__insert_file(cursor, conn, 'exe',
                            header_first=header,
                            header_second=segments,
                            import_table=sections,
                            export_table=symbols)
        return file_id

    

    def add_file(file_path):
        
        try:
            file_type = get_file_type(file_path)
            if file_type != 'application/x-dosexec' and file_type != 'application/x-executable':
                raise ValueError(f"incorrect filetype:{file_path} - type:{file_type}")
            
            if file_type == 'application/x-dosexec':
                file_id = BD_int.__insert_exe(file_path)
            elif file_type == 'application/x-executable':
                file_id = BD_int.__insert_elf(file_path)
            return file_id
        except Exception as e:
            logging.info(e)
            return -1
    def __del__(self):
        print("del")
        self.conn.close()