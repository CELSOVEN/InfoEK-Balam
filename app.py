import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import Config
from database import db
from models import Usuario


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "Debes iniciar sesión para acceder al portal."
)
login_manager.login_message_category = "warning"


@login_manager.user_loader
def cargar_usuario(usuario_id):
    return db.session.get(
        Usuario,
        int(usuario_id)
    )


@app.route("/")
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for("portal"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("portal"))

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        usuario = Usuario.query.filter_by(
            username=username
        ).first()

        if (
            usuario
            and usuario.verificar_password(password)
            and usuario.activo
        ):
            login_user(usuario)
            return redirect(url_for("portal"))

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template("login.html")


@app.route("/portal")
@login_required
def portal():
    return render_template("portal.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "La sesión se cerró correctamente.",
        "success"
    )

    return redirect(url_for("login"))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error_interno(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config["DEBUG"]
    )