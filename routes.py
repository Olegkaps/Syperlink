import os
from flask import render_template, request, flash, redirect, url_for, session, Blueprint, abort


from forms import *
from dbactions import links_db, auth_db


syperlink = Blueprint('sl', __name__)


menu = {"Сократить ссылку": "/", "Информация по ссылкам": "/links/info", "Аккаунт": "/users/profile"}
authorization_menu = {"Войти": "/users/sign_in", "Зарегистрироваться": "/users/sign_up"}


@syperlink.route("/", methods=["POST", "GET"])
def index():
    link = ""
    if 'authorised' not in session:
        flash("Добавление ссылок доступно только для авторизованных пользователей", "error")
        return redirect(url_for("sl.sign_in"))
        
    if request.method == "POST":
        link = request.form.get("link")

        short_link = links_db.add_link(link, session["id"])
        if short_link:
            link = "http://" + os.getenv("DOMAIN") + "/" + short_link.name
            flash("Успешно", "message")
        else:
            flash("Неудалось сократить ссылку", "error")
        
    return render_template("index.html", title="Сократить ссылку", menu=menu, link=link)


@syperlink.route("/<link>")
def redirect_to_real_url(link):
    url = links_db.redirect(link)
    if url:
        return redirect(url)
    else:
        abort(404)


@syperlink.route("/links/info", methods=["POST", "GET"])
def info():
    form = LinksInfoForm()
    if request.method == "POST" and form.validate_on_submit():
        links, name = links_db.get_info_links(form.Val.data)
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
            links = links_db.get_user_links(session['id'])
            return render_template("profile.html", title="Аккаунт", menu=menu, username=session['name'], links=links)
    
    return redirect(url_for("sl.sign_in"))
    


@syperlink.route("/users/sign_in", methods=["GET", "POST"])
def sign_in():
    if 'authorised' in session:
        return redirect(url_for("sl.users"))

    form = LoginForm()
    if form.validate_on_submit():
        if user := auth_db.log_in(form):
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
        new_user = auth_db.registrate(form)
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
    if auth_db.accept_email(link):
        flash("Почта успешно подтверждена, вы можете войти.", "message")
    else:
        flash("Неверная ссылка для подтверждения.", "error")
    
    return render_template("accept_email.html", title="Успешно", menu=menu)


@syperlink.route("/users/change_password", methods=["GET", "POST"])
def change_password():
    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if auth_db.change_password(form):
            flash("Письмо подтверждение отправлено на почту", "message")
        else:
            flash("Почта не найдена", "error")
        return redirect(url_for("sl.sign_in"))
    return render_template("change_password.html", title="Восстановление аккаунта", menu=menu, form=form)


@syperlink.route("/users/change_password/<name>")
def accept_password_change(name):
    if auth_db.accept_password_change(name):
        flash("Успешно", "message")
    else:
        flash("Операция отклонена", "error")

    return redirect(url_for("sl.sign_in"))