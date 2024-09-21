def login_type(login):
    # returns "username" or "email"
    if login.find('@') != -1:
        return "email"
    else:
        return "username"