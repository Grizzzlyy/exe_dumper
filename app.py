import os

from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from dotenv import load_dotenv

from logic.auth import is_user_exists, check_user_password, generate_pwd_hash, check_pwd_hash, generate_qr_code
from logic.db_users import get_user_info, add_user
from logic.db_reports import get_report
from logic.kartonn import create_report

import pyotp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signup'  # Redirect to login page if not logged in

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


# current_user from flask-login
class User(UserMixin):
    def __init__(self, username, email, has_access, is_admin):
        self.username = username
        self.email = email
        self.has_access = has_access
        self.is_admin = is_admin

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(login):
    user_info = get_user_info(login)
    if user_info is None:
        return None
    else:
        return User(user_info["username"], user_info["email"], user_info["has_access"],
                    user_info["is_admin"])


# Decorator, if first step of 2FA is completed
def pwd_correct(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user has completed 2FA
        if not session.get('is_pwd_correct'):
            flash('Wrong login or password.', 'error')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user has completed 2FA
        if not current_user.is_admin:
            return redirect(request.referrer or url_for('upload'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('signin'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists
        if is_user_exists(username):
            flash('User with this username already exists. Please choose a different one.')
            return redirect(url_for('signup'))
        elif is_user_exists(email):
            flash('User with this email already exists. Please choose a different one.')
            return redirect(url_for('signup'))

        session["is_pwd_correct"] = True
        session["username"] = username
        session["email"] = email
        session["pwd_hash"] = generate_pwd_hash(password)
        return redirect(url_for('two_fa_set'))

    return render_template('signup.html')


@app.route('/verify_2fa', methods=['POST', 'GET'])
@pwd_correct
def two_fa_verify():
    if request.method == 'POST':
        if 'verify_code' in request.form:
            code = request.form['code']
            key = session.get('2fa_key')
            if key is None:
                return redirect(url_for('two_fa_set'))

            totp = pyotp.TOTP(key)

            if totp.verify(code):
                if get_user_info(session.get('username')) is None:
                    user = {"username": session.get('username'), "email": session.get('email'),
                            "pwd_hash": session.get('pwd_hash'), "has_access": True, "is_admin": False, "2fa_key": session.get('2fa_key')}
                    add_user(user)
                user = User(session.get('username'), session.get('email'), has_access=True, is_admin=False)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid code. Please try again.')

    return render_template('2fa_verify.html')

@app.route('/set_2fa', methods=['POST', 'GET'])
@pwd_correct
def two_fa_set():
    if request.method == 'POST':
        if 'generate_qr' in request.form:
            username = session.get('username')

            user_key = pyotp.random_base32()
            session['2fa_key'] = user_key

            qr_code_path = generate_qr_code(user_key, username, 'ExeDumper.ru')
            return render_template('2fa_gen.html', qr_code=qr_code_path)

        if 'verify_code' in request.form:
            username = session.get('username')
            os.remove(f"static/tmp/{username}_qr.png")
            return redirect(url_for('two_fa_verify'))

    return render_template('2fa_gen.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        if 'login' in request.form and 'password' in request.form:
            login = request.form['login']
            password = request.form['password']

            if check_user_password(login, password):
                user_info = get_user_info(login)

                session["is_pwd_correct"] = True
                session["username"] = user_info["username"]
                session["email"] = user_info["email"]
                session["2fa_key"] = user_info["2fa_key"]

                if session.get("2fa_key") is None:
                    return redirect(url_for('two_fa_set'))
                return redirect(url_for('two_fa_verify'))
            else:
                flash('Invalid login or password. Please try again.')

    return render_template('signin.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))

        report_id = create_report(current_user.username, file)
        flash('File successfully uploaded')
        return redirect(url_for('show_report', report_id=report_id))

    return render_template('upload.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('signin'))


# TODO
@app.route('/history')
@login_required
def history():
    return render_template('upload.html')


@app.route('/report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def show_report(report_id):
    report = get_report(current_user.username, report_id)
    return render_template('report.html', report=report)


# Download binary from report
@app.route('/uploads/<string:username>/<string:filename>')
@login_required
def get_binary(username, filename):
    dir = os.path.join(UPLOADS_DIR, current_user.username)
    return send_from_directory(dir, filename)


# TODO
@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    pass


if __name__ == '__main__':
    app.run(debug=True)
