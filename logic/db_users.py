from werkzeug.security import generate_password_hash
from logic.utils import login_type

tmp_db = [
    {"username": "alice", "email": "alice@mail.com", "pwd_hash": generate_password_hash('alice'),
     "has_access": True, "is_admin": True},
    {"username": "bob", "email": "bob@mail.com", "pwd_hash": generate_password_hash('bob'),
     "has_access": True, "is_admin": False},
    {"username": "clark", "email": "clark@mail.com", "pwd_hash": generate_password_hash('clark'),
     "has_access": True, "is_admin": False},
]


def get_user_info(login):
    if login_type(login) == "username":
        for usr in tmp_db:
            if usr["username"] == login:
                return usr
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
    tmp_db.append(user)


def get_user_email(login):
    user_info = get_user_info(login)
    return user_info["email"]
