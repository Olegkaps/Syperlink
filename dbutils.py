from datetime import timedelta
from dotenv import load_dotenv
from database import *
from sqlalchemy import func


load_dotenv()

redis_time = timedelta(seconds=30) #change
redis_accept_email_time = timedelta(days=1) 


def link2redis(link):
    return "l_" + link


def confirm2redis(token):
    pass

def link_generator():
    length = int(os.getenv("TOKEN_LENGTH"))
    chars = os.getenv("CHARACTERS")
    n = db.session.query(func.count(Link.name)).scalar()
    while True:
        link = ""
        for _ in range(length):
            ind = n % len(chars)
            link += chars[ind]
            n //= len(chars)
            if n == 0:
                break
        n += 1
        yield link
