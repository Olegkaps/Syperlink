from sqlalchemy import Integer, String, ForeignKey, MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os

metadata = MetaData()
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base, metadata=metadata, engine_options={"echo": True})

class User(db.Model):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  login: Mapped[str] = mapped_column(String(12))
  email: Mapped[str] = mapped_column(String(320))
  password: Mapped[str] = mapped_column(String(162))
  is_confirmed: Mapped[bool] = mapped_column()
  is_blocked: Mapped[bool] = mapped_column()
  
  def __repr__(self):
    return f"<User '{self.login}' {self.id}>"



class Link(db.Model):
  __tablename__ = "link"

  name: Mapped[str] = mapped_column(String(os.getenv("TOKEN_LENGTH")), primary_key=True)
  url: Mapped[str] = mapped_column(String(300))
  user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

  def __repr__(self):
    return f" {self.name} {self.url} "