import secrets
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from os import getenv

from bs4 import BeautifulSoup as bs
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


def gen_otp(length=6):
    symbols = string.digits + string.ascii_uppercase
    otp = ''.join(secrets.choice(symbols) for _ in range(length))
    return otp


def send_mail(email, FROM, TO, msg):
    password = getenv("MAIL_PWD")

    server = smtplib.SMTP_SSL("smtp.yandex.ru")
    server.login(email, password)
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()


def send_otp_code(usermail, email=getenv("MAIL_ADDR")):
    code = gen_otp()

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((str(Header("ExeDumper", 'utf-8')), "exe.dumper@yandex.ru"))
    msg["To"] = usermail
    msg["Subject"] = "ExeDumper authentication code"

    html = open("templates/auth_mail_template.html").read()
    html = bs(html, "html.parser")
    html.strong.string.replace_with(code)
    html.prettify(formatter="html")
    text = ('Your code:\n{}'.format(code))

    text_part = MIMEText(text, "plain")
    html_part = MIMEText(html, "html")

    msg.attach(text_part)
    msg.attach(html_part)

    send_mail(email, email, usermail, msg)
    return generate_pwd_hash(code)
