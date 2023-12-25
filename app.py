from flask import Flask
from flask import redirect, render_template, request
from Db import db
from Db.models import users, articles
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


app = Flask(__name__)

app.secret_key = '123'
user_db = 'julia_rgz'
host_ip = '127.0.0.1'
host_port = '5434'
database_name = 'orm_rgz'
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


@app.route("/glavn")
def glavn():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "Аноним"

    return render_template('index.html', username=username)


@app.route("/check")
def main():
    my_users = users.query.all()
    print(my_users)
    return "result in console!"

def save_photo(photo):
    # Генерируем уникальное имя файла
    if current_user.is_authenticated:
        photo_filename = str(photo.filename) + str(current_user.id)
    else:
        # Обработка для анонимного пользователя
        photo_filename = "filename.jpg"
    
    # Определяем путь для сохранения файла
    photo_path = os.path.join('static', photo_filename)

    # Сохраняем файл на сервере
    photo.save(photo_path)

    # Возвращаем имя сохраненного файла
    return photo_filename


@app.route('/registr', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("glavn"))

    error = ''

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        username = request.form['username']
        photo = request.files['photo']
        mail = request.form['mail']
        about = request.form['about']
        
        if not login:
            error = 'Заполните поле "Логин".'
        elif not password:
            error = 'Заполните поле "Пароль".'
        elif not username:
            error = 'Заполните поле "Имя".'
        elif not photo:
            error = 'Выберите фотографию в поле "Фотография".'
        elif not mail:
            error = 'Заполните поле "Почта".'
        else:
            hashed_password = generate_password_hash(password)
            photo_filename = save_photo(photo)

            new_user = users(
                login = login,
                password=hashed_password,
                username=username,
                photo=photo_filename,
                mail = mail,
                about=about 
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('registr.html', error=error)


    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("glavn"))

    error = ''  # Инициализируем переменную error перед использованием

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        user = users.query.filter_by(login=login).first()#поиск пользователя в базе данных по login и получение 
        #первого совпадения с помощью метода first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("glavn"))
            else:
                error = 'Неверный пароль'
        else:
            error = 'Пользователь не найден'

    return render_template('login.html', error_message=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('glavn'))


@app.route("/articles")
@login_required
def article_list():
    my_articles = articles.query.filter_by(username=current_user.username).all()
    return render_template('list_articles.html', articles=my_articles)

@app.route("/add_article", methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == "GET":
        return render_template("add_article.html")
    
    title_form = request.form.get("title")
    text_form = request.form.get("text")
    u_mail = current_user.mail

    # Создание новой статьи
    new_article = articles(username=current_user.username, title=title_form, article_text=text_form, mail=u_mail)
    db.session.add(new_article)
    db.session.commit()

    return redirect(url_for("article_list"))


@app.route("/articles/<int:article_id>")
@login_required
def view_article(article_id):
    article = articles.query.get(article_id)
    if not article:
        return "Статья не найдена"
    return render_template("article_details.html", article=article)


@app.route("/list_articles")
def list_articles():
    all_articles = articles.query.all()
    return render_template("article_list.html", articles=all_articles)