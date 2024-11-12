import os

from flask import Flask, render_template, request, flash, redirect, url_for
from forms import *
from database import *


menu = {"Главная": "/", "Информация по ссылкам": "/links/info", "Аккаунт": "/users/profile"}
authorization_menu = {"Войти": "/users/sign_in", "Зарегистрироваться": "/users/sign_up"}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DBASE_ADRESS')
db.init_app(app)

ISDEBUG = True # False for relesae server


@app.route("/", methods=["POST", "GET"])
def index():
    link = ""
    if request.method == "POST":
        link = request.form.get("link")
        flash("Успешно", "message")
        #TO DO: check is link really exsist
        #and return new short link
        
    return render_template("index.html", title="Главная", menu=menu, link=link)


@app.route("/<link>")
def redirect_to_real_url(link):
    #get from DB and redirect
    pass


@app.route("/links/info")
def info():
    return render_template("info.html", title="Информация по ссылкам", menu=menu)


@app.route("/users/profile", methods=["POST", "GET"])
def users():
    #if not authorized
    return render_template("profile.html", title="Аккаунт", menu=menu)
    #else
    return redirect(url_for("sign_in"))


@app.route("/users/sign_in", methods=["GET", "POST"])
def sign_in():
    #if authorized
    form = LoginForm()
    if form.validate_on_submit():
        #DB actions
        return redirect("/users/profile")
    

    return render_template("sign-in.html", title="Войти", menu=menu, auth_menu=authorization_menu, form=form)
    return redirect(url_for("/users/profile")) #if authoreised


@app.route("/users/sign_up", methods=["GET", "POST"])
def sign_up():
    #if not authorized
    form = RegistrationForm()
    if form.validate_on_submit():
        #DB actions
        flash("Успешная регистрация", "message")
        redirect(url_for("/users/accept"))
        
    return render_template("sign-up.html", title="Зарегистрироваться", menu=menu, auth_menu=authorization_menu, form=form)
    return redirect(url_for("/users/profile")) #if authorised
    

@app.route("/users/accept", methods=["GET", "POST"])
def accept_email():
    # Подтвердить почту
    pass


@app.route("/users/change_password", methods=["GET", "POST"])
def change_password():
    # Сменить пароль через почту
    pass


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Не найдено", menu=menu), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=ISDEBUG , port=57)
