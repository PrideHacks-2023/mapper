from flask import Flask, request, redirect, url_for, render_template
import flask_login
import bcrypt

from dotenv import load_dotenv
from datetime import datetime
import os

import utils

dotenv_path = '.env'
load_dotenv(dotenv_path)
SECRET_KEY = os.environ.get("SECRET_KEY")

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = flask_login.LoginManager()

login_manager.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    username = request.form['username']
    password = str.encode(request.form['password'])
    password_confirm = str.encode(request.form['confirm'])
    if password != password_confirm:
        return render_template('signup.html', message="Passwords must match.")

    if utils.create_user(username, bcrypt.hashpw(password, bcrypt.gensalt())):
        return redirect(url_for('login'))

    return render_template('signup.html', message="Username already taken.")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    try:
        if utils.login_user(username, request.form['password']):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
    except TypeError:
        return render_template('login.html', message="Invalid username and/or password.")


@app.route('/message', methods=['GET', 'POST'])
@flask_login.login_required
def message():
    msg_obj = {"username": flask_login.current_user.id,
               "text": request.form['message'],
               "location": request.form['location'],
               "timestamp": datetime.now()}
    if utils.add_message(msg_obj):
        return render_template('index.html', message="Post sent successfully!")
    return render_template('index.html', message="Message not sent, no hate speech allowed", failed=True)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if not utils.check_user(username):
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if not utils.check_user(username):
        return

    user = User()
    user.id = username
    return user


if __name__ == ' __main__':
    app.debug = True
    app.run()
