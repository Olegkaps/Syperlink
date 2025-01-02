from dotenv import load_dotenv
import os

from flask import Flask


from database import db
from routes import syperlink
from dbactions import mail

load_dotenv()

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
mail.init_app(app)

ISDEBUG = True # False for relesae server


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=ISDEBUG, host='0.0.0.0', port='5000')
