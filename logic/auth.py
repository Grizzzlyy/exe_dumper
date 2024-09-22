from werkzeug.security import generate_password_hash, check_password_hash

from logic.db_users import get_user_info


def generate_pwd_hash(password):
    return generate_password_hash(password)


def check_pwd_hash(hash, pwd):
    return check_password_hash(hash, pwd)


def is_user_exists(login):
    if get_user_info(login) is None:
        return False
    return True


def check_user_password(login, password):
    # login: username or email
    # password: user password
    # Returns True is password is correct
    user_info = get_user_info(login)
    if user_info is None:
        return False

    return check_pwd_hash(user_info["pwd_hash"], password)


def send_otp_code(email='hello@mail.ru'):
    # Generate code, send it to email and return hash
    return generate_pwd_hash('123456')

