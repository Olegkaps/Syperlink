from database import *
from redis import Redis
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_


from dbutils import *
from mail import mailer


class DBManager():
    def __init__(self, r):
        self.link_gen = link_generator()
        self.redis = r

class Authorization(DBManager):
    def log_in(self, form): 
        val = form.val.data
        user = db.session.execute(db.select(User).\
                                  where(or_(User.login == val, User.email == val))).scalar()
        
        db_logger.info(f"Trying log in user {val} by {form.password.data}")
        if user and check_password_hash(user.password, form.password.data) and user.is_confirmed and not user.is_blocked:
            db_logger.info(f"User {val} authorised")
            return user
        
    def registrate(self, form):
        user = db.session.execute(db.select(User).\
                                  where(or_(User.login == form.login.data, User.email == form.email.data))).scalar()
        if user:
            db_logger.info(f"User {form.login.data} or {form.email.data} already exists, registration denied")
            return None

        new_user = User(login=form.login.data,
                        email=form.email.data,
                        password=generate_password_hash(form.password.data),
                        is_confirmed=False,
                        is_blocked=False)

        link = self.link_to_accept_email(new_user.email)

        db.session.add(new_user)
        mailer.accept_registration(new_user, link)
        db.session.commit()
        db_logger.info(f"User <{form.login.data} {form.email.data}> successfully registrated")
        return new_user

    def change_password(self, form):
        psw = generate_password_hash(form.password.data)
        email = form.email.data
        if not db.session.execute(db.select(User).where(User.email == email)).scalar():
            return False
        db_logger.info(f"User {email} tries change password")

        link = self.link_to_accept_email(email)      
        self.redis.setex(email, redis_accept_email_time, psw)
        mailer.change_password(link, email)

        return True

    def accept_password_change(self, name):
        email = self.redis.get(name)
        if email:
            password = self.redis.get(email)
            if password == None:
                db_logger.error(f"Redis has link '{name}' to change password, but don`t have password value")
            db.session.execute(db.update(User).\
                               values(password=password).\
                                where(User.email == email))
            db.session.commit()
            self.redis.delete(name)
            self.redis.delete(email)
            db_logger.info(f"User {email} succesfully changed password")
            return True
        db_logger.info(f"No link '{name}' to accept password change")
        return False

    def link_to_accept_email(self, email):
        link = str(hash(email))
        self.redis.setex(link, redis_accept_email_time, email)
        return link

    def accept_email(self, link):
        email = self.redis.get(link)
        if email:
            db.session.execute(db.update(User).\
                               values(is_confirmed=True).\
                               where(User.email == email))
            db.session.commit()
            self.redis.delete(link)
            db_logger.info(f"User {email} succesfully confirmed registration")
            return True
        db_logger.info(f"No link '{link}' to confirm registration")
        
    
class Links(DBManager):
    def add_link(self, link, id):
        user = db.session.execute(db.select(User).where(User.id == id)).scalar()
        if user and user.is_confirmed and not user.is_blocked:
            new_link = Link(name=next(self.link_gen),
                            url=link, user_id=id)
            db.session.add(new_link)
            db.session.commit()
            db_logger.info(f"User {id} successfully shortened link")
            self.redis.setex(link2redis(new_link.name), redis_time, new_link.url)
            return new_link
        db_logger.info(f"User {id} failed to shorten link")
        
    def redirect(self, link_name):
        if not (link:=self.redis.get(link2redis(link_name))):
            link = db.session.execute(db.select(Link).\
                                      where(Link.name == link_name)).scalar()
            if link:
                if link.is_blocked:
                    db_logger.info(f"link {link.name} is blocked, redirect denied")
                    return
                user = db.session.execute(db.select(User).\
                                          where(User.id == link.user_id)).scalar()
                if user == None:
                    db_logger.critical(f"link {link_name} belongs to unexisted user {link.user_id}")
                if user.is_blocked:
                    db_logger.info(f"user {user.id} is blocked, redirect denied")
                    db.session.execute(db.update(Link).\
                                       values(is_blocked=True).\
                                        where(Link.user_id == user.id))
                    db.session.commit()
                    return
                self.redis.setex(link2redis(link_name), redis_time, link.url)
                link = link.url
        return link
    
    def get_user_links(self, id):
        links = db.session.execute(db.select(Link).where(Link.user_id == id)).all()
        db_logger.info(f"User {id} has {len(links)} links")
        return links
    
    def get_info_links(self, val):
        user = db.session.execute(db.select(User).\
                                where(or_(User.email == val, User.login == val))).scalar()
        if user:
            links = db.session.execute(db.select(Link).\
                                    where(Link.user_id == user.id)).all()
        else:
            links = []
        db_logger.info(f"User {val} has {len(links)} links")
        return links, val


r = Redis(host="redis", port=6379, decode_responses=True)
auth_db = Authorization(r)
links_db = Links(r)