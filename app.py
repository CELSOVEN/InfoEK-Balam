import os
import re

from models import Contenido, Pozo, Usuario
from contenido_inicial import CONTENIDOS_INICIALES
from datos_pozos import POZOS_INICIALES

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
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


def cargar_contenidos_iniciales():
    nuevos = 0
    for datos in CONTENIDOS_INICIALES:
        existe = Contenido.query.filter_by(slug=datos["slug"]).first()
        if existe:
            continue
        db.session.add(Contenido(**datos))
        nuevos += 1
    if nuevos:
        db.session.commit()


def cargar_pozos_iniciales():
    existentes = {
        pozo.pozos.strip().lower(): pozo
        for pozo in Pozo.query.all()
        if pozo.pozos
    }

    for datos in POZOS_INICIALES:
        identificador = datos["pozos"].strip().lower()
        pozo = existentes.get(identificador)

        if pozo is None:
            db.session.add(Pozo(**datos))
            continue

        for campo, valor in datos.items():
            setattr(pozo, campo, valor)

    db.session.commit()


db.init_app(app)

with app.app_context():
    db.create_all()
    cargar_contenidos_iniciales()
    cargar_pozos_iniciales()

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

    carpeta_biblioteca = os.path.join(app.root_path, "Biblioteca")
    documentos_biblioteca = []

    if os.path.isdir(carpeta_biblioteca):
        documentos_biblioteca = sorted(
            archivo
            for archivo in os.listdir(carpeta_biblioteca)
            if archivo.lower().endswith(".pdf")
            and os.path.isfile(os.path.join(carpeta_biblioteca, archivo))
        )

    return render_template(
        "portal.html",
        contenidos=contenidos,
        documentos_biblioteca=documentos_biblioteca,
    )


@app.route("/biblioteca/<path:nombre_archivo>")
@login_required
def ver_documento_biblioteca(nombre_archivo):
    carpeta_biblioteca = os.path.join(app.root_path, "Biblioteca")

    return send_from_directory(
        carpeta_biblioteca,
        nombre_archivo,
        as_attachment=False,
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
        termino_lower = termino.lower()

        resultados_contenido = (
            Contenido.query
            .filter(
                Contenido.activo.is_(True),
                db.or_(
                    db.func.lower(Contenido.titulo).contains(termino_lower),
                    db.func.lower(Contenido.categoria).contains(termino_lower),
                    db.func.lower(Contenido.resumen).contains(termino_lower),
                    db.func.lower(Contenido.contenido).contains(termino_lower),
                    db.func.lower(Contenido.palabras_clave).contains(termino_lower),
                )
            )
            .order_by(Contenido.orden)
            .all()
        )

        resultados_pozos = (
            Pozo.query
            .filter(
                Pozo.activo.is_(True),
                db.or_(
                    db.func.lower(Pozo.nombre).contains(termino_lower),
                    db.func.lower(Pozo.plataforma).contains(termino_lower),
                    db.func.lower(Pozo.pozos).contains(termino_lower),
                    db.func.lower(Pozo.coordenadas_utm).contains(termino_lower),
                    db.func.lower(Pozo.tipo_perforacion).contains(termino_lower),
                    db.func.lower(Pozo.tipo).contains(termino_lower),
                    db.func.lower(Pozo.servicio).contains(termino_lower),
                    db.func.lower(Pozo.palabras_clave).contains(termino_lower),
                )
            )
            .order_by(Pozo.plataforma, Pozo.nombre)
            .all()
        )
    else:
        resultados_contenido = []
        resultados_pozos = []

    return render_template(
        "busqueda.html",
        termino=termino,
        resultados_contenido=resultados_contenido,
        resultados_pozos=resultados_pozos,
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
