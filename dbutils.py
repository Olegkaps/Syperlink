from datetime import timedelta
from dotenv import load_dotenv
from database import *
from sqlalchemy import func


from logger import Logger

load_dotenv()

db_logger = Logger.get_logger("DB")

redis_time = timedelta(minutes=30) 
redis_accept_email_time = timedelta(days=1) 


def link2redis(link):
    return "l_" + link


def link_generator():
    length = int(os.getenv("TOKEN_LENGTH"))
    chars = os.getenv("CHARACTERS")
    n = db.session.query(func.count(Link.name)).scalar()
    db_logger.info(f"link generator initialised with {n} value")
    while True:
        link = ""
        for _ in range(length):
            ind = n % len(chars)
            link += chars[ind]
            n //= len(chars)
            if n == 0:
                break
        n += 1
        db_logger.info(f"link {n} generated")
        yield link
