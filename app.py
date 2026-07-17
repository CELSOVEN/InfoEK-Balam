import os
import re

from models import Contenido, Usuario

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


PLATAFORMAS_BUSQUEDA = {
    "EK-A": {
        "nombre": "EK-A",
        "imagen": "01_EK-A.png",
    },
    "BALAM-TB": {
        "nombre": "Balam-TB",
        "imagen": "02_BALAM-TB.png",
    },
    "BALAM-A": {
        "nombre": "Balam-A",
        "imagen": "03_BALAM-A.png",
    },
    "EK-A2": {
        "nombre": "EK-A2",
        "imagen": "04_EK-A2.png",
    },
    "EK-TA": {
        "nombre": "EK-TA",
        "imagen": "05_EK-TA.png",
    },
    "BALAM-TE": {
        "nombre": "Balam-TE",
        "imagen": "06_BALAM-TE.png",
    },
    "BALAM-TA": {
        "nombre": "Balam-TA",
        "imagen": "07_BALAM-TA.png",
    },
    "BALAM-TA2": {
        "nombre": "Balam-TA2",
        "imagen": "08_BALAM-TA2.png",
    },
    "EK-TB": {
        "nombre": "EK-TB",
        "imagen": "09_EK-TB.png",
    },
    "BALAM-TD": {
        "nombre": "Balam-TD",
        "imagen": "10_BALAM-TD.png",
    },
}


def buscar_plataforma(termino):
    termino_normalizado = termino.upper().replace("_", "-")

    for clave in sorted(PLATAFORMAS_BUSQUEDA, key=len, reverse=True):
        patron = rf"(?<![A-Z0-9]){re.escape(clave)}(?![A-Z0-9])"
        if re.search(patron, termino_normalizado):
            return PLATAFORMAS_BUSQUEDA[clave]

    return None

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
    contenidos = (
        Contenido.query
        .filter_by(activo=True)
        .order_by(Contenido.orden)
        .all()
    )

    total_secciones = len(contenidos)

    return render_template(
        "portal.html",
        contenidos=contenidos,
        total_secciones=total_secciones
    )

@app.route("/contenido/<string:slug>")
@login_required
def ver_contenido(slug):
    contenido = Contenido.query.filter_by(
        slug=slug,
        activo=True
    ).first_or_404()

    contenidos_menu = (
        Contenido.query
        .filter_by(activo=True)
        .order_by(Contenido.orden)
        .all()
    )

    return render_template(
        "contenido.html",
        contenido=contenido,
        contenidos_menu=contenidos_menu
    )

@app.route("/buscar")
@login_required
def buscar():
    termino = request.args.get(
        "q",
        ""
    ).strip()

    resultados = []
    resultado_plataforma = None

    if termino:
        resultado_plataforma = buscar_plataforma(termino)
        patron = f"%{termino}%"

        resultados = (
            Contenido.query
            .filter(
                Contenido.activo.is_(True),
                db.or_(
                    Contenido.titulo.ilike(patron),
                    Contenido.categoria.ilike(patron),
                    Contenido.resumen.ilike(patron),
                    Contenido.contenido.ilike(patron),
                    Contenido.palabras_clave.ilike(patron),
                )
            )
            .order_by(Contenido.orden)
            .all()
        )

    return render_template(
        "busqueda.html",
        termino=termino,
        resultados=resultados,
        resultado_plataforma=resultado_plataforma,
    )


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
