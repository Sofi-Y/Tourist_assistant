import os
import sys
import requests
import sqlite3
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PIL import Image
# from pytesseract import pytesseract
from googletrans import Translator
from flask import Flask, render_template, redirect
import argparse
from io import BytesIO
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import datetime
from flask import Flask, redirect, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# http://127.0.0.1:5000/reg
SqlAlchemyBase = dec.declarative_base()

__factory = None

def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


# global_init("users1.db")


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class RegisterForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')

    
# Предполагает запуск python3 main_project_file.py Москва
parser = argparse.ArgumentParser(
    description="accepts args")
parser.add_argument("toponym", help='Название объекта или адрес')
args = parser.parse_args()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

SCREEN_SIZE = [600, 450]

toponym_to_find = toponym

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    pass

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

delta = "0.005"

map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([delta, delta]),
    "l": "map"
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)

im = Image.open(BytesIO(
    response.content))
im.save('map.png')


@app.route("/")
def index():
    return render_template("project_template.html", txt=TXT)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg1.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        session = create_session()
        # if session.query(User).filter(User.email == form.email.data).first():
            # return render_template('register.html', title='Регистрация', form=form,
                                   # message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            about=form.about.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/users')
    return render_template('reg1.html', title='Регистрация', form=form)


@app.route('/users')
def users():
    con = sqlite3.connect("users11.db")
    cur = con.cursor()
    res = cur.execute("""SELECT * FROM users""").fetchall()
    s = []
    for x in res:
        d = dict()
        d['id'] = x[0]
        d['name'] = x[1]
        d['about'] = x[2]
        d['hashed_password'] = x[3]
        d['created_date'] = x[4]
        s.append(d)    
    return render_template("temp.html", base=s)
    

def main():
    global_init("users11.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    app1 = QApplication(sys.argv)
    ex = Example(ll, scale)
    # ex.show()
    main()
    sys.exit(app1.exec())
