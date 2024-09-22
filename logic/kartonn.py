import datetime
import os
from werkzeug.utils import secure_filename

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


def create_report(username, file):
    # Get info from karton
    # Save that info to database
    # return id of created report

    filename = secure_filename(file.filename)
    dir = os.path.join(UPLOADS_DIR, username)
    os.makedirs(dir, exist_ok=True)
    file.save(os.path.join(dir, filename))

    return 150
