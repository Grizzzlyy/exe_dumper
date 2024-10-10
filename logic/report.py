"""
Report logic
"""

import os

from werkzeug.utils import secure_filename

from back.BD_interface import BD_int

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


def create_report(username, file):
    filename = secure_filename(file.filename)
    dir = os.path.join(UPLOADS_DIR, username)
    os.makedirs(dir, exist_ok=True)
    file.save(os.path.join(dir, filename))
    worker = BD_int()
    file_id = worker.add_file(username, os.path.join(dir, filename))
    if file_id == -1:
        os.remove(os.path.join(dir, filename))
    return file_id
