"""
Flask-login logic
"""

from flask_login import UserMixin, LoginManager
from logic.db_users import get_user_info

login_manager = LoginManager()


def init(app, login_view):
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'signup'  # Redirect to login page if not logged in


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
