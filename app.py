import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user

from logic.auth import is_user_exists, check_user_password, generate_pwd_hash, check_pwd_hash, send_otp_code
from logic.db_users import get_user_info, add_user, change_user_access, get_list_of_users, get_history, create_api_token, get_filename
from logic.report import create_report
from logic import user_manage
from logic import api
from back.parse_file import get_chunk
from logic.frontend import get_report_info, format_hex

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

user_manage.init(app, 'signup')
api.init(app)

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


# Decorator, if first step of 2FA is completed but second isn't
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
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if the user has completed 2FA
        if not current_user.is_admin:
            return redirect(request.referrer or url_for('upload'))
        return f(*args, **kwargs)

    return decorated_function


# Check if user is logged in and has access
def access_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if the user has completed 2FA
        if not current_user.has_access:
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
                user_info = get_user_info(session.get('username'))
                user = user_manage.User(user_info["username"], user_info["email"], user_info["has_access"],
                                        user_info["is_admin"])
                login_user(user)  # Login user
                return redirect(url_for('index'))
            else:
                flash('Invalid code. Please try again.')

    return render_template('verification.html')


@app.route('/upload', methods=['GET', 'POST'])
@access_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))

        file_id = create_report(current_user.username, file)
        if file_id == -1:
            flash('Incorrect file type')
            return redirect(url_for('upload'))

        flash('File successfully uploaded')
        return redirect(url_for('show_report', file_id=file_id))

    return render_template('upload.html')


@app.route('/logout')
@access_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('signin'))


@app.route('/history')
@access_required
def history():
    history_dict = get_history(current_user.username)
    return render_template('history.html', history=history_dict)


@app.route('/report/<int:file_id>', methods=['GET', 'POST'])
@access_required
def show_report(file_id):
    report = get_report_info(file_id)
    return render_template('report.html', report=report, file_id=file_id)


@app.route('/hex/<int:file_id>', methods=['GET'])
@access_required
def get_hex_chunk(file_id):
    chunk_idx = request.args.get('chunk_idx', 0, type=int)
    file_name = get_filename(current_user.username,file_id)
    chunk = get_chunk(chunk_idx, f'./files/{current_user.username}/{file_name}')

    if chunk is None:
        return jsonify({'formatted_hex': None})  # No more chunks to load

    # Format the hex and ASCII representation of the chunk
    formatted_hex = format_hex(chunk_idx, chunk)

    return jsonify(formatted_hex)


# Download binary from report
@app.route('/uploads/<int:file_id>')
@access_required
def get_binary(file_id):
    filename = get_filename(current_user.username, file_id)
    dir = os.path.join(UPLOADS_DIR, current_user.username)
    return send_from_directory(dir, filename)

@app.route('/profile')
@access_required
def profile():
    api_key = create_api_token(current_user.username)
    #TODO сохранять в бд, если его там нет и доставать от туда
    profile_info = {"api_key": 'Bearer ' + api_key}
    return render_template('profile.html', profile_info=profile_info)


@app.route('/admin_panel')
@admin_required
def admin_panel():
    users = get_list_of_users()
    return render_template('admin_panel.html', users=users)


@app.route('/block/<string:username>', methods=['POST'])
@admin_required
def block_user(username):
    change_user_access(username, ban=True)
    flash(f"User '{username}' has been blocked.", 'success')
    return redirect(url_for('admin_panel'))


@app.route('/unblock/<string:username>', methods=['POST'])
@admin_required
def unblock_user(username):
    change_user_access(username, ban=False)
    flash(f"User '{username}' has been unblocked.", 'success')
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)
