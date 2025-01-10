import os

from dotenv import load_dotenv
from flask_mail import Message, Mail
from flask import render_template


from logger import Logger

mail_logger = Logger.get_logger("MAIL")

load_dotenv()


class Mailer():
    def __init__(self, email):
        self.mail = Mail()
        self.email = email

    def init_app(self, app):
        self.mail.init_app(app)

    def accept_registration(self, new_user, link):
        link = "http://" + os.getenv("DOMAIN") + \
            "/users/accept/" + link

        msg = Message( subject=f"Подтверждение регистрации",
            sender=self.email,
            recipients=[new_user.email],
            )
        
        msg.html = render_template("accept_email_email.html", user=new_user, link=link)
        self.mail.send(msg)
        mail_logger.info(f"Send {link} to {new_user.email}")

    def change_password(self, link, email):
        link = "http://" + os.getenv("DOMAIN") + \
            "/users/change_password/" + link
        
        msg = Message( subject=f"Подтверждение смены пароля",
            sender="kapshaioleg@yandex.ru",
            recipients=[email],
            )
        msg.html = render_template("change_password_mail.html", link=link)
        self.mail.send(msg)
        mail_logger.info(f"Send {link} to {email}")



mailer = Mailer(email="kapshaioleg@yandex.ru")