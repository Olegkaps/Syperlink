from dotenv import load_dotenv
import os

from flask import Flask, render_template


from database import db
from routes import syperlink, menu
from mail import mailer

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DBASE_ADRESS')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_NAME')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

    app.register_blueprint(syperlink)

    db.init_app(app)
    mailer.init_app(app)

    return app

ISDEBUG = True # False for relesae server

app = create_app()


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Не найдено", menu=menu), 404


if __name__ == "__main__":
    app.run(debug=ISDEBUG)
