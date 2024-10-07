from werkzeug.security import generate_password_hash
from logic.utils import login_type
from back.BD_interface import BD_int

def get_user_info(login):
    worker = BD_int()
    if login_type(login) == 'username':
        if worker.user_exists(username=login):
            return worker.get_user_info()
        return None
    elif login_type(login) == 'email':
        if worker.user_exists(email=login):
            return worker.get_user_info()
        return None
    else:
        # ERROR
        raise ValueError(f"login type is {login_type(login)}")


def add_user(user):
    worker = BD_int()
    worker.add_user(user["username"],user["email"],user["pwd_hash"])


def get_user_email(login):
    worker = BD_int()
    email = worker.get_email(login)
    return email
