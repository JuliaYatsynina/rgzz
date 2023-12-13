from flask import Flask
from flask import redirect, Blueprint, render_template, request
from Db import db
from Db.models import users
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

app.secret_key = '123'
user_db = 'rgz_orm'
host_ip = '127.0.0.1'
host_port = '5434'
database_name = 'rgz_julia'
password = '123'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_users(user_id):
    return users.query.get(int(user_id))


@app.route("/")
def lab6_view():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "Аноним"

    return render_template("index.html", username=username)