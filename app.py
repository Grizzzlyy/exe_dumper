from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# Simulated in-memory storage
users = {
    'admin': {'password': generate_password_hash('adminpass'), 'is_admin': True, 'email_verified': False},
    'user1': {'password': generate_password_hash('user1pass'), 'is_admin': False, 'email_verified': False}
}

reports = {
    'user1': [{'id': 1, 'name': 'report1.bin', 'hash': 'abc123', 'size': '2MB', 'type': 'binary', 'date_submitted': '2024-09-18'}]
}

class User(UserMixin):
    """User class with id as the username and is_admin for role management."""
    def __init__(self, username, is_admin=False, email_verified=False):
        self.id = username
        self.is_admin = is_admin
        self.email_verified = email_verified

@login_manager.user_loader
def load_user(username):
    if username in users:
        user_info = users[username]
        return User(username, user_info['is_admin'], user_info['email_verified'])
    return None

def admin_required(f):
    """Decorator to ensure only admins can access certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You do not have permission to access this page.", 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username, users[username]['is_admin'], users[username]['email_verified'])
            login_user(user)
            session['two_factor_verified'] = False  # Reset 2FA status

            # Simulate 2FA by sending an email with a dummy code (e.g., '123456')
            session['two_factor_code'] = '123456'
            flash('A 2FA code has been sent to your email. Please enter it to continue.', 'info')
            return redirect(url_for('two_factor_auth'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/two_factor_auth', methods=['GET', 'POST'])
@login_required
def two_factor_auth():
    if request.method == 'POST':
        code = request.form['code']
        if code == session.get('two_factor_code'):
            session['two_factor_verified'] = True
            users[current_user.id]['email_verified'] = True  # Simulate email verification
            return redirect(url_for('upload'))
        else:
            flash('Invalid 2FA code.', 'danger')
    return render_template('two_factor_auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/upload')
@login_required
def upload():
    if not session.get('two_factor_verified'):
        flash('Please complete 2FA to access the application.', 'danger')
        return redirect(url_for('two_factor_auth'))
    return render_template('upload.html')

@app.route('/history')
@login_required
def history():
    user_reports = reports.get(current_user.id, [])
    return render_template('history.html', reports=user_reports)

@app.route('/report/<int:report_id>')
@login_required
def report(report_id):
    user_reports = reports.get(current_user.id, [])
    report = next((r for r in user_reports if r['id'] == report_id), None)
    if report:
        return render_template('report.html', report=report)
    flash("You don't have access to this report.", 'danger')
    return redirect(url_for('history'))

@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)
