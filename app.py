import os

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv

from logic.auth import is_user_exists, send_otp_code, check_user_password
from logic.manage_db import get_user_info, add_user, get_user_email

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signup'  # Redirect to login page if not logged in

UPLOADS_DIR = os.getenv("UPLOADS_DIR")


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

# If first step of 2FA is completed
def pwd_correct(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user has completed 2FA
        if not session.get('is_pwd_correct'):
            flash('Wrong login or password.', 'error')
            return redirect(url_for('signin'))
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
            flash('User with this username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))
        elif is_user_exists(email):
            flash('User with this email already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))

        flash('You have successfully signed up! Please verify your email.', 'success')
        session["is_pwd_correct"] = True
        session["username"] = username
        session["email"] = email
        session["pwd_hash"] = generate_password_hash(password)
        return redirect(url_for('verify_email'))

    return render_template('signup.html')


@app.route('/verify_email', methods=['GET', 'POST'])
@pwd_correct
def verify_email():
    if request.method == 'POST':
        if 'send_code' in request.form:
            session['otp_code_hash'] = send_otp_code(session.get('email'))
            flash(f"OTP code has been sent to your email {session.get('email')}.")  # Simulate by showing it in flash
            return redirect(url_for('verify_email'))
        elif 'verify_code' in request.form:
            code = request.form['code']
            code_hash = session.get('otp_code_hash')

            if check_password_hash(code_hash, code):
                flash('Email verified')
                # Add user to database
                user = {"username": session.get('username'), "email": session.get('email'),
                        "pwd_hash": session.get('pwd_hash'),
                        "has_access": True, "is_admin": False}
                add_user(user)

                session.pop('username', None)
                session.pop('email', None)
                session.pop('pwd_hash', None)
                session.pop('is_pwd_correct', None)
                return redirect(url_for('signin'))
            else:
                flash('Invalid code. Please try again.')

    return render_template('verify_email.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        if 'login' in request.form and 'password' in request.form:
            # User login phase
            login = request.form['login']
            password = request.form['password']

            if check_user_password(login, password):
                user_info = get_user_info(login)

                session["is_pwd_correct"] = True
                session["username"] = user_info["username"]
                session["email"] = user_info["email"]

                return redirect(url_for('two_factor_auth'))
            else:
                flash('Invalid login or password. Please try again.')

    return render_template('signin.html')


@app.route('/two_factor_auth', methods=['GET', 'POST'])
@pwd_correct
def two_factor_auth():
    if request.method == 'POST':
        if 'send_code' in request.form:
            session['otp_code_hash'] = send_otp_code(session.get('email'))
            flash(f"OTP code has been sent to your email {session.get('email')}.")  # Simulate by showing it in flash
            return redirect(url_for('two_factor_auth'))
        elif 'verify_code' in request.form:
            code = request.form['code']
            code_hash = session.get('otp_code_hash')
            if code_hash is None:
                flash("You didn't request 2FA code!")
                return redirect(url_for('two_factor_auth'))
            if check_password_hash(code_hash, code):
                flash('2FA successful!')
                user = User(session.get('username'), session.get('email'), True, False)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid code. Please try again.')

    return render_template('two_factor_auth.html')





@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload'))

        file = request.files['the_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, filename))
        flash('File successfully uploaded')
        return redirect(url_for('upload'))

        f.save(os.path.join(UPLOADS_DIR, current_user.username, )'/var/www/uploads/uploaded_file.txt')
    return render_template('upload.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('signin'))

@app.route('/history')
@login_required
def history():
    return render_template('upload.html')


# @app.route('/signup', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         login_user(current_user)
#
#         flask.flash('Logged in successfully.')
#
#         next = flask.request.args.get('next')
#         # url_has_allowed_host_and_scheme should check if the url is safe
#         # for redirects, meaning it matches the request host.
#         # See Django's url_has_allowed_host_and_scheme for an example.
#         if not url_has_allowed_host_and_scheme(next, request.host):
#             return flask.abort(400)
#
#         return flask.redirect(next or flask.url_for('index'))
#     return render_template('login.html', form=form)
#
#
# def admin_required(f):
#     """Decorator to ensure only admins can access certain routes."""
#
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated or not current_user.is_admin:
#             flash("You do not have permission to access this page.", 'danger')
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# @app.route('/')
# def index():
#     if current_user.is_authenticated:
#         return redirect(url_for('upload'))
#     return redirect(url_for('login'))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         if username in users and check_password_hash(users[username]['password'], password):
#             user = User(username, users[username]['is_admin'], users[username]['email_verified'])
#             login_user(user)
#             session['two_factor_verified'] = False  # Reset 2FA status
#
#             # Simulate 2FA by sending an email with a dummy code (e.g., '123456')
#             session['two_factor_code'] = '123456'
#             flash('A 2FA code has been sent to your email. Please enter it to continue.', 'info')
#             return redirect(url_for('two_factor_auth'))
#         else:
#             flash('Invalid username or password', 'danger')
#
#     return render_template('login.html')
#
#
# @app.route('/two_factor_auth', methods=['GET', 'POST'])
# @login_required
# def two_factor_auth():
#     if request.method == 'POST':
#         code = request.form['code']
#         if code == session.get('two_factor_code'):
#             session['two_factor_verified'] = True
#             users[current_user.id]['email_verified'] = True  # Simulate email verification
#             return redirect(url_for('upload'))
#         else:
#             flash('Invalid 2FA code.', 'danger')
#     return render_template('two_factor_auth.html')
#
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out.')
#     return redirect(url_for('login'))
#
#
# @app.route('/upload')
# @login_required
# def upload():
#     if not session.get('two_factor_verified'):
#         flash('Please complete 2FA to access the application.', 'danger')
#         return redirect(url_for('two_factor_auth'))
#     return render_template('upload.html')
#
#
# @app.route('/history')
# @login_required
# def history():
#     user_reports = reports.get(current_user.id, [])
#     return render_template('history.html', reports=user_reports)
#
#
# @app.route('/report/<int:report_id>')
# @login_required
# def report(report_id):
#     user_reports = reports.get(current_user.id, [])
#     report = next((r for r in user_reports if r['id'] == report_id), None)
#     if report:
#         return render_template('report.html', report=report)
#     flash("You don't have access to this report.", 'danger')
#     return redirect(url_for('history'))
#
#
# @app.route('/admin_panel')
# @login_required
# @admin_required
# def admin_panel():
#     return render_template('admin_panel.html')


if __name__ == '__main__':
    app.run(debug=True)
