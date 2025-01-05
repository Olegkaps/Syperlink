from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


_req = "Заполните поле"
_log = "Длина логина от 3 до 12 символов"
_psw_re = "Пароль должен содержать как минимум одну цифру и букву  и несодержать служебных символов"
_psw_len = "Пароль должен быть не короче 10 символов"

_min_log = 3
_max_log = 12
_min_psw = 10
_max_psw = 40


class LoginForm(FlaskForm):
    login = StringField("Логин", [DataRequired(message=_req), 
                                  Length(min=_min_log, max=_max_log, message=_log)])
    password = PasswordField("Пароль", [DataRequired(message=_req),
                                        Length(min=_min_psw, max=_max_psw, message=_psw_len)])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    login = StringField("Логин", [DataRequired(message=_req), 
                                  Length(min=_min_log, max=_max_log, message=_log)])
    password = PasswordField("Пароль", [DataRequired(message=_req), 
                                        Length(min=_min_psw, max=_max_psw, message=_psw_len),
                                        EqualTo("password2", message="Пароли должны свопадать"),
                                        Regexp(r"([a-zA-Z]*\d)|(\d*[a-zA-Z])", message=_psw_re)])
    password2 = PasswordField("Повторите пароль")
    email = StringField("Почта", [DataRequired(message=_req), 
                                  Email(message="Неверный адрес почты")])
    submit = SubmitField("Зарегистрироваться")


class LinksInfoForm(FlaskForm):
    Val = StringField("Имя или логин", [DataRequired(message=_req)])
    submit = SubmitField("Найти")