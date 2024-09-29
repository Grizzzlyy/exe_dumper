import BD_interface
import sqlite3
import json


BD_interface.add_file('A:\\Lessons\\BIP\\elf-Linux-ARM64-bash')

conn = sqlite3.connect('BD/files.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM files')
files = cursor.fetchall()
for file in files:
    print(f"ID: {file[0]}, Type: {file[1]}")
    print(f"Header: {json.loads(file[2])}")
    print(f"second Header: {json.loads(file[3])}")
    print(f"Import Table: {json.loads(file[4])}")
    print(f"Export Table: {json.loads(file[5])}")
    print()