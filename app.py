import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from functools import wraps

from models import (
    Contenido,
    Permiso,
    Pozo,
    ProduccionPozoMensual,
    Rol,
    SesionNavegacion,
    Usuario,
)
from contenido_inicial import CONTENIDOS_INICIALES
from datos_pozos import POZOS_INICIALES

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
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

PERMISOS_INICIALES = {
    "biblioteca.ver": (
        "Consultar biblioteca",
        "Permite listar y visualizar los PDF sin mostrar la opción de descarga.",
    ),
    "biblioteca.descargar": (
        "Descargar biblioteca",
        "Permite descargar y guardar los documentos PDF de la biblioteca.",
    ),
    "produccion.ver": (
        "Consultar producción",
        "Permite consultar el histórico y la API de producción.",
    ),
    "usuarios.administrar": (
        "Administrar usuarios y roles",
        "Permite crear roles y asignarlos a los usuarios.",
    ),
}

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

HISTORIALES_PRODUCCION = {
    "Balam-A": "Balam-A_HistorialProduccion.png",
    "Balam-TA": "Balam-TA_HistorialProduccion.png",
    "Balam-TA2": "Balam-TA2_HistorialProduccion.png",
    "Balam-TB": "Balam-TB_HistorialProduccion.png",
    "Balam-TE": "Balam-TE_HistorialProduccion.png",
    "Ek-A": "EK-A_HistorialProduccion.png",
    "Ek-A2": "EK-A2_HistorialProduccion.png",
    "Ek-TA": "EK-TA_HistorialProduccion.png",
    "Ek-TB": "EK-TB_HistorialProduccion.png",
}


VARIABLES_PRODUCCION = {
    "gas": {
        "columna": ProduccionPozoMensual.gas_mmpcd,
        "etiqueta": "GAS (MPCD)",
    },
    "agua": {
        "columna": ProduccionPozoMensual.agua_mbd,
        "etiqueta": "AGUA (MBD)",
    },
    "aceite": {
        "columna": ProduccionPozoMensual.aceite_mbd,
        "etiqueta": "ACEITE (MBD)",
    },
    "goc": {
        "columna": ProduccionPozoMensual.gor_pc_bbl,
        "etiqueta": "GOR (pcd/bd)",
    },
    "gor": {
        "columna": ProduccionPozoMensual.gor_pc_bbl,
        "etiqueta": "GOR (pcd/bd)",
    },
}

DIMENSIONES_PRODUCCION = {
    "total": [],
    "campo": [ProduccionPozoMensual.campo],
    "plataforma": [ProduccionPozoMensual.campo, ProduccionPozoMensual.plataforma],
    "pozo": [
        ProduccionPozoMensual.campo,
        ProduccionPozoMensual.plataforma,
        ProduccionPozoMensual.pozo,
    ],
}


def normalizar_lista_parametros(nombre):
    valores = request.args.getlist(nombre)
    if not valores:
        valor = request.args.get(nombre, "")
        valores = valor.split(",") if valor else []
    return [valor.strip().upper() for valor in valores if valor.strip()]


def clave_resultado_variable(variable):
    return "goc" if variable == "gor" else variable


def fila_tiene_valores_positivos(fila, variables):
    for variable in variables:
        valor = fila.get(clave_resultado_variable(variable), 0)
        try:
            if float(valor or 0) > 0:
                return True
        except (TypeError, ValueError):
            continue
    return False


def recortar_filas_a_periodos_productivos(filas, variables, intervalo):
    if intervalo == "total" or not filas or not any("periodo" in fila for fila in filas):
        return filas, None

    periodos_productivos = [
        fila["periodo"]
        for fila in filas
        if fila.get("periodo") and fila_tiene_valores_positivos(fila, variables)
    ]

    if not periodos_productivos:
        return [], "sin_valores"

    periodo_inicio = min(periodos_productivos)
    periodo_fin = max(periodos_productivos)
    filas_recortadas = [
        fila
        for fila in filas
        if periodo_inicio <= fila.get("periodo", "") <= periodo_fin
    ]

    if len(filas_recortadas) == len(filas):
        return filas, None

    return filas_recortadas, "recortado"


def fecha_periodo(intervalo):
    if intervalo == "anio":
        return db.func.strftime("%Y", ProduccionPozoMensual.fecha)
    if intervalo == "mes":
        return db.func.strftime("%Y-%m", ProduccionPozoMensual.fecha)
    return None


def periodo_representativo(intervalo):
    anio = db.func.strftime("%Y", ProduccionPozoMensual.fecha)
    mes = db.cast(db.func.strftime("%m", ProduccionPozoMensual.fecha), db.Integer)

    if intervalo == "anio":
        return anio
    if intervalo == "trimestre":
        trimestre = db.case(
            (mes <= 3, "T1"),
            (mes <= 6, "T2"),
            (mes <= 9, "T3"),
            else_="T4",
        )
        return db.func.printf("%s-%s", anio, trimestre)
    if intervalo == "semestre":
        semestre = db.case(
            (mes <= 6, "S1"),
            else_="S2",
        )
        return db.func.printf("%s-%s", anio, semestre)
    return None


def opciones_produccion():
    campos = [
        valor[0]
        for valor in db.session.query(ProduccionPozoMensual.campo)
        .distinct()
        .order_by(ProduccionPozoMensual.campo)
        .all()
    ]
    plataformas = [
        {
            "campo": valor.campo,
            "nombre": valor.plataforma,
        }
        for valor in db.session.query(
            ProduccionPozoMensual.campo.label("campo"),
            ProduccionPozoMensual.plataforma.label("plataforma"),
        )
        .distinct()
        .order_by(
            ProduccionPozoMensual.campo,
            ProduccionPozoMensual.plataforma,
        )
        .all()
    ]
    pozos = [
        {
            "campo": valor.campo,
            "plataforma": valor.plataforma,
            "nombre": valor.pozo,
        }
        for valor in db.session.query(
            ProduccionPozoMensual.campo.label("campo"),
            ProduccionPozoMensual.plataforma.label("plataforma"),
            ProduccionPozoMensual.pozo.label("pozo"),
        )
        .distinct()
        .order_by(
            ProduccionPozoMensual.campo,
            ProduccionPozoMensual.plataforma,
            ProduccionPozoMensual.pozo,
        )
        .all()
    ]
    rango = db.session.query(
        db.func.min(ProduccionPozoMensual.fecha),
        db.func.max(ProduccionPozoMensual.fecha),
    ).first()

    return {
        "campos": campos,
        "plataformas": plataformas,
        "pozos": pozos,
        "fecha_min": rango[0].isoformat() if rango and rango[0] else "",
        "fecha_max": rango[1].isoformat() if rango and rango[1] else "",
        "total_registros": ProduccionPozoMensual.query.count(),
    }


def buscar_plataforma(termino):
    termino_normalizado = termino.upper().replace("_", "-")

    for clave in sorted(PLATAFORMAS_BUSQUEDA, key=len, reverse=True):
        patron = rf"(?<![A-Z0-9]){re.escape(clave)}(?![A-Z0-9])"
        if re.search(patron, termino_normalizado):
            return PLATAFORMAS_BUSQUEDA[clave]

    return None


def obtener_pozos_por_plataforma():
    pozos_por_plataforma = {}
    pozos = (
        Pozo.query
        .filter_by(activo=True)
        .order_by(
            Pozo.plataforma,
            db.case(
                (db.func.lower(Pozo.servicio) == "production", 0),
                (
                    db.func.lower(Pozo.servicio).in_(("injection", "inyection")),
                    1,
                ),
                (db.func.lower(Pozo.elemento) == "center of structure", 2),
                else_=1,
            ),
            Pozo.servicio,
            Pozo.pozos,
        )
        .all()
    )

    for pozo in pozos:
        pozos_por_plataforma.setdefault(
            pozo.plataforma,
            []
        ).append(pozo)

    return pozos_por_plataforma


def obtener_imagenes_por_plataforma(pozos_por_plataforma):
    return {
        plataforma: PLATAFORMAS_BUSQUEDA.get(
            plataforma.upper(),
            {}
        ).get("imagen")
        for plataforma in pozos_por_plataforma
    }


def obtener_historiales_por_plataforma(pozos_por_plataforma=None):
    plataformas = (
        pozos_por_plataforma
        if pozos_por_plataforma is not None
        else HISTORIALES_PRODUCCION
    )
    return {
        plataforma: HISTORIALES_PRODUCCION[plataforma]
        for plataforma in plataformas
        if plataforma in HISTORIALES_PRODUCCION
    }


def cargar_contenidos_iniciales():
    existentes = {
        contenido.slug: contenido
        for contenido in Contenido.query.all()
    }

    for datos in CONTENIDOS_INICIALES:
        contenido = existentes.get(datos["slug"])

        if contenido is None:
            db.session.add(Contenido(**datos))
            continue

        for campo, valor in datos.items():
            setattr(contenido, campo, valor)

    db.session.commit()


def cargar_pozos_iniciales():
    existentes = {
        pozo.nombre.strip().lower(): pozo
        for pozo in Pozo.query.all()
        if pozo.nombre
    }

    nombres_vigentes = {
        datos["nombre"].strip().lower() for datos in POZOS_INICIALES
    }

    for identificador, pozo in existentes.items():
        if identificador not in nombres_vigentes:
            pozo.activo = False

    for datos in POZOS_INICIALES:
        identificador = datos["nombre"].strip().lower()
        pozo = existentes.get(identificador)

        if pozo is None:
            db.session.add(Pozo(**datos))
            continue

        for campo, valor in datos.items():
            setattr(pozo, campo, valor)

    db.session.commit()


def cargar_roles_y_permisos_iniciales():
    permisos = {}
    for codigo, (nombre, descripcion) in PERMISOS_INICIALES.items():
        permiso = Permiso.query.filter_by(codigo=codigo).first()
        if permiso is None:
            permiso = Permiso(codigo=codigo)
            db.session.add(permiso)
        permiso.nombre = nombre
        permiso.descripcion = descripcion
        permisos[codigo] = permiso

    administrador = Rol.query.filter_by(nombre="Administrador").first()
    if administrador is None:
        administrador = Rol(nombre="Administrador", es_sistema=True)
        db.session.add(administrador)
    administrador.descripcion = "Acceso completo a todas las características."
    administrador.permisos = list(permisos.values())

    lector = Rol.query.filter_by(nombre="Lector").first()
    if lector is None:
        lector = Rol(nombre="Lector", es_sistema=True)
        db.session.add(lector)
    lector.descripcion = "Acceso de consulta, incluida la biblioteca."
    lector.permisos = [
        permisos["biblioteca.ver"],
        permisos["produccion.ver"],
    ]

    basico = Rol.query.filter_by(nombre="Básico").first()
    if basico is None:
        basico = Rol(nombre="Básico", es_sistema=True)
        db.session.add(basico)
    basico.descripcion = "Acceso al portal y consulta de la biblioteca."
    basico.permisos = [
        permisos["biblioteca.ver"],
    ]

    db.session.flush()
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    for usuario in Usuario.query.all():
        if usuario.username == admin_username:
            if administrador not in usuario.roles:
                usuario.roles.append(administrador)
        elif not usuario.roles:
            # Conserva el acceso que tenían antes de incorporar RBAC.
            usuario.roles.append(lector)
    db.session.commit()


db.init_app(app)

with app.app_context():
    db.create_all()
    # SQLite no agrega columnas nuevas mediante create_all. Esta migración
    # conserva las instalaciones existentes sin requerir Flask-Migrate.
    columnas_pozo = {
        columna[1]
        for columna in db.session.execute(db.text("PRAGMA table_info(pozos)"))
    }
    if "elemento" not in columnas_pozo:
        db.session.execute(db.text("ALTER TABLE pozos ADD COLUMN elemento VARCHAR(250)"))
        db.session.commit()
    cargar_contenidos_iniciales()
    cargar_pozos_iniciales()
    cargar_roles_y_permisos_iniciales()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "Debes iniciar sesión para acceder al portal."
)
login_manager.login_message_category = "warning"


@app.template_filter("fecha_local")
def fecha_local(fecha):
    if fecha is None:
        return "—"
    fecha_utc = fecha.replace(tzinfo=timezone.utc)
    return fecha_utc.astimezone(
        timezone(timedelta(hours=-6))
    ).strftime("%d/%m/%Y %H:%M:%S")


@app.template_filter("duracion_legible")
def duracion_legible(segundos):
    horas, resto = divmod(int(segundos), 3600)
    minutos, segundos = divmod(resto, 60)
    if horas:
        return f"{horas} h {minutos} min {segundos} s"
    if minutos:
        return f"{minutos} min {segundos} s"
    return f"{segundos} s"


@login_manager.user_loader
def cargar_usuario(usuario_id):
    return db.session.get(
        Usuario,
        int(usuario_id)
    )


def permiso_requerido(codigo):
    def decorador(vista):
        @wraps(vista)
        @login_required
        def vista_protegida(*args, **kwargs):
            if not current_user.tiene_permiso(codigo):
                abort(403)
            return vista(*args, **kwargs)

        return vista_protegida

    return decorador


@app.before_request
def registrar_actividad_usuario():
    if not current_user.is_authenticated:
        return
    registro_id = session.get("registro_acceso_id")
    if not registro_id:
        return

    ahora_epoch = time.time()
    ultima_actualizacion = session.get("registro_actividad_epoch", 0)
    if ahora_epoch - ultima_actualizacion < 60:
        return

    registro = db.session.get(SesionNavegacion, registro_id)
    if registro and registro.usuario_id == current_user.id and not registro.fecha_salida:
        registro.ultima_actividad = datetime.utcnow()
        db.session.commit()
        session["registro_actividad_epoch"] = ahora_epoch


@app.route("/")
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for("portal"))

    return redirect(url_for("login"))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


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
            ahora = datetime.utcnow()
            registro = SesionNavegacion(
                usuario=usuario,
                fecha_ingreso=ahora,
                ultima_actividad=ahora,
            )
            db.session.add(registro)
            db.session.commit()
            session["registro_acceso_id"] = registro.id
            session["registro_actividad_epoch"] = time.time()
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

    documentos_biblioteca = []
    puede_ver_biblioteca = current_user.tiene_permiso("biblioteca.ver")
    carpeta_biblioteca = os.path.join(app.root_path, "Biblioteca")
    if puede_ver_biblioteca and os.path.isdir(carpeta_biblioteca):
        documentos_biblioteca = sorted(
            archivo
            for archivo in os.listdir(carpeta_biblioteca)
            if archivo.lower().endswith(".pdf")
            and os.path.isfile(os.path.join(carpeta_biblioteca, archivo))
        )

    pozos_por_plataforma = obtener_pozos_por_plataforma()
    imagenes_por_plataforma = obtener_imagenes_por_plataforma(
        pozos_por_plataforma
    )
    historiales_por_plataforma = obtener_historiales_por_plataforma(
        pozos_por_plataforma
    )

    return render_template(
        "portal.html",
        contenidos=contenidos,
        documentos_biblioteca=documentos_biblioteca,
        puede_ver_biblioteca=puede_ver_biblioteca,
        puede_descargar_biblioteca=current_user.tiene_permiso(
            "biblioteca.descargar"
        ),
        pozos_por_plataforma=pozos_por_plataforma,
        imagenes_por_plataforma=imagenes_por_plataforma,
        historiales_por_plataforma=historiales_por_plataforma,
        total_pozos=db.session.query(
            db.func.coalesce(db.func.sum(Pozo.numero_pozos), 0)
        ).filter(
            Pozo.activo.is_(True),
            db.func.lower(Pozo.servicio) == "production",
        ).scalar(),
        opciones_produccion=opciones_produccion(),
    )


@app.route("/biblioteca/<path:nombre_archivo>")
@permiso_requerido("biblioteca.ver")
def ver_documento_biblioteca(nombre_archivo):
    if not nombre_archivo.lower().endswith(".pdf"):
        abort(404)

    return render_template(
        "visor_biblioteca.html",
        nombre_archivo=nombre_archivo,
        puede_descargar=current_user.tiene_permiso("biblioteca.descargar"),
    )


@app.route("/biblioteca/visualizar-archivo/<path:nombre_archivo>")
@permiso_requerido("biblioteca.ver")
def archivo_biblioteca_visualizacion(nombre_archivo):
    if not nombre_archivo.lower().endswith(".pdf"):
        abort(404)
    carpeta_biblioteca = os.path.join(app.root_path, "Biblioteca")

    respuesta = send_from_directory(
        carpeta_biblioteca,
        nombre_archivo,
        as_attachment=False,
    )
    respuesta.headers["Cache-Control"] = "no-store, private, max-age=0"
    respuesta.headers["Pragma"] = "no-cache"
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    return respuesta


@app.route("/biblioteca/descargar/<path:nombre_archivo>")
@permiso_requerido("biblioteca.descargar")
def descargar_documento_biblioteca(nombre_archivo):
    if not nombre_archivo.lower().endswith(".pdf"):
        abort(404)
    carpeta_biblioteca = os.path.join(app.root_path, "Biblioteca")
    return send_from_directory(
        carpeta_biblioteca,
        nombre_archivo,
        as_attachment=True,
        download_name=os.path.basename(nombre_archivo),
    )


@app.route("/produccion/historica")
@permiso_requerido("produccion.ver")
def produccion_historica():
    return render_template(
        "produccion_historica.html",
        opciones_produccion=opciones_produccion(),
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

    pozos_por_plataforma = (
        obtener_pozos_por_plataforma()
        if slug == "well-master-files"
        else {}
    )
    imagenes_por_plataforma = obtener_imagenes_por_plataforma(
        pozos_por_plataforma
    )
    historiales_por_plataforma = obtener_historiales_por_plataforma(
        None if slug == "production-history" else pozos_por_plataforma
    )

    return render_template(
        "contenido.html",
        contenido=contenido,
        contenidos_menu=contenidos_menu,
        pozos_por_plataforma=pozos_por_plataforma,
        imagenes_por_plataforma=imagenes_por_plataforma,
        historiales_por_plataforma=historiales_por_plataforma,
        opciones_produccion=opciones_produccion(),
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
    pozos_resultado_plataforma = {}
    imagenes_resultado_plataforma = {}

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
                    db.func.lower(Pozo.elemento).contains(termino_lower),
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

        if resultado_plataforma:
            plataforma_buscada = resultado_plataforma["nombre"].upper()
            pozos_por_plataforma = obtener_pozos_por_plataforma()
            pozos_resultado_plataforma = {
                plataforma: pozos
                for plataforma, pozos in pozos_por_plataforma.items()
                if plataforma.upper() == plataforma_buscada
            }
            imagenes_resultado_plataforma = obtener_imagenes_por_plataforma(
                pozos_resultado_plataforma
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
        pozos_resultado_plataforma=pozos_resultado_plataforma,
        imagenes_resultado_plataforma=imagenes_resultado_plataforma,
    )


@app.route("/api/produccion")
@permiso_requerido("produccion.ver")
def api_produccion():
    nivel = request.args.get("nivel", "campo")
    intervalo = request.args.get("intervalo", "semestre")
    variables = [
        variable.lower()
        for variable in normalizar_lista_parametros("variables")
    ] or [
        "aceite",
        "agua",
        "gas",
        "goc",
    ]

    if nivel not in DIMENSIONES_PRODUCCION:
        return {"error": "Nivel de consulta no valido."}, 400
    if intervalo not in {"total", "anio", "trimestre", "semestre"}:
        return {"error": "Intervalo de consulta no valido."}, 400

    variables = [variable for variable in variables if variable in VARIABLES_PRODUCCION]
    if not variables:
        return {"error": "Selecciona al menos una variable valida."}, 400

    parametros_filtros = {
        "campo": normalizar_lista_parametros("campo"),
        "plataforma": normalizar_lista_parametros("plataforma"),
        "pozo": normalizar_lista_parametros("pozo"),
    }

    if len(parametros_filtros["campo"]) > 1:
        return {"error": "Selecciona un solo campo para esta consulta."}, 400
    if nivel != "total" and len(parametros_filtros["campo"]) != 1:
        return {"error": "Selecciona un campo para esta consulta."}, 400
    if nivel == "plataforma" and len(parametros_filtros["plataforma"]) != 1:
        return {"error": "Selecciona una sola plataforma para esta consulta."}, 400
    if nivel == "pozo":
        if len(parametros_filtros["plataforma"]) != 1:
            return {"error": "Selecciona una plataforma antes de consultar por pozo."}, 400
        if len(parametros_filtros["pozo"]) != 1:
            return {"error": "Selecciona un solo pozo para esta consulta."}, 400

    filtros_por_nivel = {
        "total": [
            (ProduccionPozoMensual.campo, "campo"),
            (ProduccionPozoMensual.plataforma, "plataforma"),
            (ProduccionPozoMensual.pozo, "pozo"),
        ],
        "campo": [
            (ProduccionPozoMensual.campo, "campo"),
        ],
        "plataforma": [
            (ProduccionPozoMensual.campo, "campo"),
            (ProduccionPozoMensual.plataforma, "plataforma"),
        ],
        "pozo": [
            (ProduccionPozoMensual.campo, "campo"),
            (ProduccionPozoMensual.plataforma, "plataforma"),
            (ProduccionPozoMensual.pozo, "pozo"),
        ],
    }

    condiciones = []

    for columna, nombre_parametro in filtros_por_nivel[nivel]:
        valores = parametros_filtros[nombre_parametro]
        if valores:
            condiciones.append(columna.in_(valores))

    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    if fecha_inicio:
        condiciones.append(ProduccionPozoMensual.fecha >= fecha_inicio)
    if fecha_fin:
        condiciones.append(ProduccionPozoMensual.fecha <= fecha_fin)

    periodo = fecha_periodo(intervalo)
    columnas = []
    agrupaciones = []
    dimensiones = DIMENSIONES_PRODUCCION[nivel]

    if intervalo in {"anio", "trimestre", "semestre"}:
        periodo = db.func.strftime("%Y-%m", ProduccionPozoMensual.fecha)
        periodo_grupo = periodo_representativo(intervalo)
        columnas_ultimo_mes = []
        grupos_ultimo_mes = []

        if periodo_grupo is not None:
            columnas_ultimo_mes.append(periodo_grupo.label("periodo_grupo"))
            grupos_ultimo_mes.append(periodo_grupo)

        for dimension in dimensiones:
            columnas_ultimo_mes.append(dimension.label(dimension.key))
            grupos_ultimo_mes.append(dimension)

        columnas_ultimo_mes.append(
            db.func.max(ProduccionPozoMensual.fecha).label("fecha_representativa")
        )
        consulta_ultimo_mes = db.session.query(*columnas_ultimo_mes)
        if condiciones:
            consulta_ultimo_mes = consulta_ultimo_mes.filter(*condiciones)
        if grupos_ultimo_mes:
            consulta_ultimo_mes = consulta_ultimo_mes.group_by(*grupos_ultimo_mes)
        ultimo_mes = consulta_ultimo_mes.subquery("ultimo_mes")

        condiciones_union = [
            ProduccionPozoMensual.fecha == ultimo_mes.c.fecha_representativa
        ]
        if periodo_grupo is not None:
            condiciones_union.append(
                periodo_grupo == ultimo_mes.c.periodo_grupo
            )
        for dimension in dimensiones:
            condiciones_union.append(dimension == getattr(ultimo_mes.c, dimension.key))

        columnas.append(periodo.label("periodo"))
        agrupaciones.append(periodo)
        consulta = (
            db.session.query(*columnas)
            .select_from(ProduccionPozoMensual)
            .join(ultimo_mes, db.and_(*condiciones_union))
        )
    else:
        if periodo is not None:
            columnas.append(periodo.label("periodo"))
            agrupaciones.append(periodo)
        consulta = db.session.query(*columnas)

    columnas.extend(dimensiones)
    agrupaciones.extend(dimensiones)

    for variable in variables:
        columna = VARIABLES_PRODUCCION[variable]["columna"]
        if variable in {"goc", "gor"}:
            gas_pcd = db.func.sum(ProduccionPozoMensual.gas_mmpcd) * 1000000
            aceite_bd = db.func.sum(ProduccionPozoMensual.aceite_mbd) * 1000
            columnas.append((gas_pcd / db.func.nullif(aceite_bd, 0)).label("goc"))
        elif variable == "gas":
            columnas.append((db.func.sum(columna) * 1000).label(variable))
        else:
            columnas.append(db.func.sum(columna).label(variable))

    consulta = consulta.with_entities(*columnas)
    if condiciones:
        consulta = consulta.filter(*condiciones)

    notas = []
    if intervalo == "anio":
        notas.append(
            "Intervalo anual: se muestra el último mes disponible de cada año "
            "dentro de la selección; no se acumulan los meses."
        )
    elif intervalo == "trimestre":
        notas.append(
            "Intervalo trimestral: se muestra el último mes disponible de cada "
            "trimestre dentro de la selección; no se acumulan los meses."
        )
    elif intervalo == "semestre":
        notas.append(
            "Intervalo semestral: se muestra el último mes disponible de cada "
            "semestre dentro de la selección; no se acumulan los meses."
        )
    elif intervalo == "total":
        notas.append(
            "Intervalo total: se muestra el acumulado de las fechas "
            "seleccionadas."
        )

    if agrupaciones:
        consulta = consulta.group_by(*agrupaciones).order_by(*agrupaciones)

    filas = [dict(fila._mapping) for fila in consulta.all()]
    for fila in filas:
        for clave, valor in list(fila.items()):
            if hasattr(valor, "isoformat"):
                fila[clave] = valor.isoformat()
            elif valor is None:
                fila[clave] = 0
            elif isinstance(valor, float):
                fila[clave] = round(valor, 4)

    filas, ajuste_periodo = recortar_filas_a_periodos_productivos(
        filas,
        variables,
        intervalo,
    )
    if ajuste_periodo == "recortado":
        notas.append(
            "Se omitieron periodos iniciales o finales sin datos mayores a cero."
        )
    elif ajuste_periodo == "sin_valores":
        notas.append(
            "No hay datos mayores a cero en las fechas seleccionadas."
        )

    return {
        "filas": filas,
        "variables": {
            variable: VARIABLES_PRODUCCION[variable]["etiqueta"]
            for variable in variables
        },
        "nivel": nivel,
        "intervalo": intervalo,
        "notas": notas,
    }


@app.route("/administracion/roles", methods=["GET", "POST"])
@permiso_requerido("usuarios.administrar")
def administrar_roles():
    token_csrf = session.setdefault("token_csrf", secrets.token_urlsafe(32))
    if request.method == "POST":
        if not secrets.compare_digest(
            request.form.get("token_csrf", ""),
            token_csrf,
        ):
            abort(400)
        accion = request.form.get("accion")
        if accion == "crear_usuario":
            username = request.form.get("username", "").strip()
            nombre_persona = request.form.get("nombre_persona", "").strip()
            password = request.form.get("password", "")
            confirmar_password = request.form.get("confirmar_password", "")
            usuario_existente = Usuario.query.filter(
                db.func.lower(Usuario.username) == username.lower()
            ).first()

            if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", username):
                flash(
                    "El usuario debe tener entre 3 y 50 caracteres y solo puede "
                    "incluir letras, números, punto, guion o guion bajo.",
                    "danger",
                )
            elif not nombre_persona:
                flash("El nombre de la persona es obligatorio.", "danger")
            elif usuario_existente:
                flash("Ese nombre de usuario ya está registrado.", "danger")
            elif len(password) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "danger")
            elif password != confirmar_password:
                flash("Las contraseñas no coinciden.", "danger")
            else:
                ids_roles = request.form.getlist("roles", type=int)
                roles_seleccionados = Rol.query.filter(
                    Rol.id.in_(ids_roles)
                ).all()
                if not roles_seleccionados:
                    rol_basico = Rol.query.filter_by(nombre="Básico").first()
                    roles_seleccionados = [rol_basico] if rol_basico else []

                usuario = Usuario(
                    username=username,
                    nombre=nombre_persona,
                    roles=roles_seleccionados,
                )
                usuario.establecer_password(password)
                db.session.add(usuario)
                db.session.commit()
                flash(f"Usuario {nombre_persona} creado correctamente.", "success")
                return redirect(url_for("administrar_roles"))
        elif accion == "crear_rol":
            nombre = request.form.get("nombre", "").strip()
            if not nombre:
                flash("El nombre del rol es obligatorio.", "danger")
            elif Rol.query.filter(db.func.lower(Rol.nombre) == nombre.lower()).first():
                flash("Ya existe un rol con ese nombre.", "danger")
            else:
                codigos = request.form.getlist("permisos")
                rol = Rol(
                    nombre=nombre,
                    descripcion=request.form.get("descripcion", "").strip() or None,
                    permisos=Permiso.query.filter(Permiso.codigo.in_(codigos)).all(),
                )
                db.session.add(rol)
                db.session.commit()
                flash("Rol creado correctamente.", "success")
                return redirect(url_for("administrar_roles"))
        elif accion == "actualizar_usuario":
            usuario = db.session.get(Usuario, request.form.get("usuario_id", type=int))
            if usuario is None:
                abort(404)
            ids_roles = request.form.getlist("roles", type=int)
            roles_seleccionados = Rol.query.filter(Rol.id.in_(ids_roles)).all()
            conserva_administracion = any(
                permiso.codigo == "usuarios.administrar"
                for rol in roles_seleccionados
                for permiso in rol.permisos
            )
            if usuario.id == current_user.id and not conserva_administracion:
                flash(
                    "No puedes quitarte tu propio permiso de administración.",
                    "danger",
                )
                return redirect(url_for("administrar_roles"))
            password_nuevo = request.form.get("password_nuevo", "")
            if password_nuevo and len(password_nuevo) < 8:
                flash(
                    "La nueva contraseña debe tener al menos 8 caracteres.",
                    "danger",
                )
                return redirect(url_for("administrar_roles"))
            usuario.roles = roles_seleccionados
            if password_nuevo:
                usuario.establecer_password(password_nuevo)
            db.session.commit()
            flash(f"Cuenta de {usuario.nombre} actualizada.", "success")
            return redirect(url_for("administrar_roles"))

    return render_template(
        "administrar_roles.html",
        usuarios=Usuario.query.order_by(Usuario.nombre).all(),
        roles=Rol.query.order_by(Rol.nombre).all(),
        permisos=Permiso.query.order_by(Permiso.nombre).all(),
        token_csrf=token_csrf,
    )


@app.route("/administracion/actividad")
@permiso_requerido("usuarios.administrar")
def actividad_usuarios():
    pagina = max(request.args.get("pagina", 1, type=int), 1)
    paginacion = (
        SesionNavegacion.query
        .join(Usuario)
        .order_by(SesionNavegacion.fecha_ingreso.desc())
        .paginate(page=pagina, per_page=50, error_out=False)
    )
    return render_template(
        "actividad_usuarios.html",
        paginacion=paginacion,
        sesiones=paginacion.items,
    )


@app.route("/logout")
@login_required
def logout():
    registro_id = session.pop("registro_acceso_id", None)
    session.pop("registro_actividad_epoch", None)
    if registro_id:
        registro = db.session.get(SesionNavegacion, registro_id)
        if registro and registro.usuario_id == current_user.id and not registro.fecha_salida:
            ahora = datetime.utcnow()
            registro.ultima_actividad = ahora
            registro.fecha_salida = ahora
            db.session.commit()
    logout_user()

    flash(
        "La sesión se cerró correctamente.",
        "success"
    )
    return redirect(url_for("login"))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404


@app.errorhandler(403)
def acceso_denegado(error):
    return render_template("403.html"), 403


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
