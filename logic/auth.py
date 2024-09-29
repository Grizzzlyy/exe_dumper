from werkzeug.security import generate_password_hash, check_password_hash

from logic.db_users import get_user_info

import pyotp
import qrcode


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


def generate_qr_code(key, account_name, issuer_name):
    # Генерация URI для TOTP аутентификации.
    uri = pyotp.totp.TOTP(key).provisioning_uri(name=account_name, issuer_name=issuer_name)

    # Создание QR-кода.
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    # Генерация изображения QR-кода.
    img = qr.make_image()
    img.save(f'static/{account_name}_qr.png')

    return f'{account_name}_qr.png'