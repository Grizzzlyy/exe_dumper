from werkzeug.security import generate_password_hash
from logic.utils import login_type
from back.BD_interface import BD_int
from flask import jsonify
from flask_jwt_extended import create_access_token

def get_user_info(login):
    with BD_int() as worker:
        if login_type(login) == 'username':
            if worker.user_exists(login):
                return worker.get_user_info(username=login)
            return None
        elif login_type(login) == 'email':
            if worker.get_user_name('email') != None:
                return worker.get_user_info(email=login)
            return None
        else:
            # ERROR
            raise ValueError(f"login type is {login_type(login)}")


def add_user(user):
    with BD_int() as worker:
        worker.add_user(user["username"],user["email"],user["pwd_hash"])


def get_user_email(login):
    with BD_int() as worker:
        email = worker.get_email(login)
    return email

def change_user_access(username, ban):
    with BD_int() as worker:
        worker.change_user_access(username, ban)
        
def get_list_of_users():
    with BD_int() as worker:
        return worker.get_list_of_users()
    
def get_history(username):
    with BD_int() as worker:
        return worker.get_history(username)
    
def get_filename(file_idx):
    with BD_int() as worker:
        return worker.get_filename_by_idx(file_idx)

def create_token(username):
    access_token = create_access_token(identity=username)
    return access_token