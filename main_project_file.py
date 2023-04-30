import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PIL import Image
# from pytesseract import pytesseract
from googletrans import Translator
from flask import Flask, render_template
import argparse
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
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

# http://127.0.0.1:5000/register
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


global_init("users1.db")

class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')

    
# Предполагает запуск python3 main_project_file.py 23.727366,37.961127 2
parser = argparse.ArgumentParser(
    description="accepts args")
parser.add_argument("ll", help='Задайте координаты через запятую')
parser.add_argument("scale", help='Задайте масштаб (любые числа от 1.0 до 4.0)', default=1)
args = parser.parse_args()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

SCREEN_SIZE = [600, 450]
# ll = input('Задайте координаты через запятую:')
# scale = input('Задайте масштаб (любые числа от 1.0 до 4.0):')
#  23.727366,37.961127

#pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
IMG = 'map.png'



class Example(QWidget):
    def __init__(self, ll, scale):
        super().__init__()
        self.getImage()
        self.initUI()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&scale={scale}&size=600,450&spn=0.002,0.002&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # self.img = Image.open('map.png')
        # self.res = pytesseract.image_to_string(self.img)
        #self.p = Translator()
        #self.p_translated = self.p.translate(self.res, dest='russian')
        #self.translated = str(self.p_translated.text)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        # Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        #self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    # def closeEvent(self, event):
        # os.remove(self.map_file)

@app.route("/")
def index():
    return render_template("project_template.html")


@app.route("/reg")
def reg():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('project_reg_form.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('project_reg_form.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/index')
    return render_template('project_reg_form.html', title='Регистрация', form=form)


def main():
    app.run(port=8080, host='127.0.0.1')
        
        
if __name__ == '__main__':
    app1 = QApplication(sys.argv)
    ex = Example(ll, scale)
    ex.show()
    main()
    sys.exit(app1.exec())