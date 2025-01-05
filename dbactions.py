from database import *
from redis import Redis
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from dbutils import *

from dotenv import load_dotenv
from flask_mail import Message, Mail
from flask import render_template

load_dotenv()

mail = Mail()


class DBManager():
    def __init__(self):
        self.link_gen = link_generator()
        self.redis = Redis(host="redis", port=6379, decode_responses=True)

    def log_in(self, form): 
        user = db.session.execute(db.select(User).\
                                  where(User.login == form.login.data)).scalar()
        
        if user and check_password_hash(user.password, form.password.data) and user.is_confirmed and not user.is_blocked:
            return user
        
    def registrate(self, form):
        user = db.session.execute(db.select(User).\
                                  where(or_(User.login == form.login.data, User.email == form.email.data))).scalar()
        if user:
            return None

        new_user = User(login=form.login.data,
                        email=form.email.data,
                        password=generate_password_hash(form.password.data),
                        is_confirmed=False,
                        is_blocked=False)
        
        link = "http://" + os.getenv("DOMAIN") + \
            "/users/accept/" + self.link_to_accept_email(new_user.email)
            

        msg = Message( subject=f"Подтверждение регистрации",
            sender="kapshaioleg@yandex.ru",
            recipients=[new_user.email],
            )
        
        msg.html = render_template("accept_email_email.html", user=new_user, link=link)
        mail.send(msg)


        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def link_to_accept_email(self, email):
        link = str(hash(email))
        self.redis.setex(link, redis_accept_email_time, email)
        return link

    def accept_email(self, link):
        email = self.redis.get(link)
        db.session.execute(db.update(User).\
                           values(is_confirmed=True).\
                           where(User.email == email))
        db.session.commit()
        
        self.redis.delete(link)
        
    
    def add_link(self, link, id):
        user = db.session.execute(db.select(User).where(User.id == id)).scalar()
        if user and user.is_confirmed and not user.is_blocked:
            new_link = Link(name=next(self.link_gen),
                            url=link, user_id=id)
            db.session.add(new_link)
            db.session.commit()
            self.redis.setex(link2redis(new_link.name), redis_time, new_link.url)
            return new_link
        
    def redirect(self, link_name):
        if not (link:=self.redis.get(link2redis(link_name))):
            link = db.session.execute(db.select(Link).where(Link.name == link_name)).scalar()
            if link:
                link = link.url
                self.redis.setex(link2redis(link_name), redis_time, link)
        return link
    
    def get_user_links(self, id):
        links = db.session.execute(db.select(Link).where(Link.user_id == id)).all()
        return links
    
    def get_info_links(self, val):
        user = db.session.execute(db.select(User).\
                                where(or_(User.email == val, User.login == val))).scalar()
        links = db.session.execute(db.select(Link).\
                                where(Link.user_id == user.id)).all()
        return links, user.login


DB = DBManager()