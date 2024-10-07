from werkzeug.security import generate_password_hash
from logic.utils import login_type
from back.BD_interface import BD_int

tmp_db = [
    {"username": "alice", "email": "alice@mail.com", "pwd_hash": generate_password_hash('alice'),
     "has_access": True, "is_admin": True},
    {"username": "bob", "email": "bob@mail.com", "pwd_hash": generate_password_hash('bob'),
     "has_access": True, "is_admin": False},
    {"username": "clark", "email": "clark@mail.com", "pwd_hash": generate_password_hash('clark'),
     "has_access": True, "is_admin": False},
    {"username": "james", "email": "daroslav.skiba@yandex.ru", "pwd_hash": generate_password_hash('james'),
     "has_access": True, "is_admin": False},
]


def get_user_info(login):
    worker = BD_int()
    if login_type(login) == "username":
        if worker.user_exists():
            return worker.get_user_info()
        return None
    elif login_type(login) == "email":
        for usr in tmp_db:
            if usr["email"] == login:
                return usr
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
