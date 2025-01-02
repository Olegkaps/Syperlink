import os
from flask import render_template, request, flash, redirect, url_for, session, Blueprint, abort


from forms import *
from dbactions import DB


syperlink = Blueprint('sl', __name__)


menu = {"Главная": "/", "Информация по ссылкам": "/links/info", "Аккаунт": "/users/profile"}
authorization_menu = {"Войти": "/users/sign_in", "Зарегистрироваться": "/users/sign_up"}


@syperlink.route("/", methods=["POST", "GET"])
def index():
    link = ""
    if 'authorised' not in session:
        flash("Добавление ссылок доступно только для авторизованных пользователей", "error")
        return redirect(url_for("sl.sign_in"))
        
    if request.method == "POST":
        link = request.form.get("link")

        short_link = DB.add_link(link, session["id"])
        if short_link:
            link = "http://" + os.getenv("DOMAIN") + "/" + short_link.name
            flash("Успешно", "message")
        else:
            flash("Неудалось сократить ссылку", "error")
        
    return render_template("index.html", title="Главная", menu=menu, link=link)


@syperlink.route("/<link>")
def redirect_to_real_url(link):
    url = DB.redirect(link)
    if url:
        return redirect(url)
    else:
        abort(404)


@syperlink.route("/links/info", methods=["POST", "GET"])
def info():
    form = LinksInfoForm()
    if request.method == "POST" and form.validate_on_submit():
        links, name = DB.get_info_links(form.Val.data)
    else:
        name = ""
        links = []
    
    return render_template("info.html", title="Информация по ссылкам", menu=menu, links=links, name=name, form=form)


@syperlink.route("/users/profile", methods=["POST", "GET"])
def users():
    if 'authorised' in session:
        if request.method == "POST":
            del session['authorised']
            del session['name']
            del session['id']
        else:
            links = DB.get_user_links(session['id'])
            return render_template("profile.html", title="Аккаунт", menu=menu, username=session['name'], links=links)
    
    return redirect(url_for("sl.sign_in"))
    


@syperlink.route("/users/sign_in", methods=["GET", "POST"])
def sign_in():
    if 'authorised' in session:
        return redirect(url_for("sl.users"))

    form = LoginForm()
    if form.validate_on_submit():
        if user := DB.log_in(form):
            session.permanent = True
            session['authorised'] = True
            session['name'] = user.login
            session['id'] = user.id
            return redirect(url_for("sl.users"))
        else:
            flash("Неверный пароль или логин.", "error")
    

    return render_template("sign-in.html", title="Войти", menu=menu, auth_menu=authorization_menu, form=form)


@syperlink.route("/users/sign_up", methods=["GET", "POST"])
def sign_up():
    if 'authorised' in session:
        return redirect(url_for("sl.users"))

    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = DB.registrate(form)
        if new_user:

            flash("Успешная регистрация", "message")
            flash("Письмо для подтверждения регистрации отправлено на почту ", "message")
            return redirect(url_for("sl.accept_email"))
        else:
            flash("Пользователь с таким логином или почтой уже зарегистрирован", "error")
        
    return render_template("sign-up.html", title="Зарегистрироваться", menu=menu, auth_menu=authorization_menu, form=form)
    

@syperlink.route("/users/accept")
def accept_email():
    return render_template("accept_email.html", title="Успешно", menu=menu)


@syperlink.route("/users/accept/<link>")
def accept_email_link(link):
    DB.accept_email(link)
    flash("Почта успешно подтверждена, вы можете войти.", "message")
    return render_template("accept_email.html", title="Успешно", menu=menu)


@syperlink.route("/users/change_password", methods=["GET", "POST"])
def change_password():
    # Сменить пароль через почту
    pass


@syperlink.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Не найдено", menu=menu), 404



