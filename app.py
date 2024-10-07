import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user

from logic.auth import is_user_exists, check_user_password, generate_pwd_hash, check_pwd_hash, send_otp_code
# from logic.db_reports import get_report
from logic.db_users import get_user_info, add_user
from logic.kartonn import create_report
from logic import user_manage
from logic import api
from back.BD_interface import BD_int
from back.parse_file import file_to_hex, get_chunk
from logic.frontend import get_report_info, format_hex

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

user_manage.init(app, 'signup')
api.init(app)

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


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
    print(current_user.is_authenticated)  # Debugging purpose
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
        session["code_sent"] = False
        return redirect(url_for('check_mail_code'))

    return render_template('signup.html')


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
                session["code_sent"] = False

                return redirect(url_for('check_mail_code'))
            else:
                flash('Invalid login or password. Please try again.')

    return render_template('signin.html')


# Right after signup
@app.route('/verify', methods=['GET', 'POST'])
@pwd_correct
def check_mail_code():
    if not session.get('code_sent'):
        session['otp_code_hash'] = send_otp_code(session.get('email'))
        session['code_sent'] = True

    if request.method == 'POST':
        if 'send_code' in request.form:
            session['otp_code_hash'] = send_otp_code(session.get('email'))
        elif 'verify_code' in request.form:
            code = request.form['code']
            code_hash = session.get('otp_code_hash')

            if check_pwd_hash(code_hash, code):
                if not is_user_exists(session.get('username')):
                    # Add user to database
                    user = {"username": session.get('username'), "email": session.get('email'),
                            "pwd_hash": session.get('pwd_hash'), "has_access": True, "is_admin": False}
                    add_user(user)

                user = user_manage.User(session.get('username'), session.get('email'), has_access=True, is_admin=False)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid code. Please try again.')

    return render_template('verification.html')


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


@app.route('/report/<int:file_id>', methods=['GET', 'POST'])
@login_required
def show_report(file_id):
    report = get_report_info(file_id)
    return render_template('report_new.html', report=report, file_id=file_id)


@app.route('/hex/<int:file_id>', methods=['GET'])
@login_required
def get_hex_chunk(file_id):
    chunk_idx = request.args.get('chunk_idx', 0, type=int)

    chunk = get_chunk(chunk_idx, "./files/HxD.exe")

    if chunk is None:
        return jsonify({'formatted_hex': None})  # No more chunks to load

    # Format the hex and ASCII representation of the chunk
    formatted_hex = format_hex(chunk_idx, chunk)

    return jsonify(formatted_hex)


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
