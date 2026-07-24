import os

from app import app
from database import db

from contenido_inicial import CONTENIDOS_INICIALES
from datos_pozos import POZOS_INICIALES
from datos_produccion import leer_produccion_excel
from models import Usuario, Contenido, Pozo, ProduccionPozoMensual, Rol


def crear_usuario_administrador():
    """
    Crea el usuario administrador si aún no existe.
    """

    admin_username = os.environ.get(
        "ADMIN_USERNAME",
        "administrator"
    )

    admin_name = os.environ.get(
        "ADMIN_NAME",
        "Administrador"
    )

    usuario = Usuario.query.filter_by(
        username=admin_username
    ).first()

    if usuario:
        rol_administrador = Rol.query.filter_by(nombre="Administrador").first()
        if rol_administrador and rol_administrador not in usuario.roles:
            usuario.roles.append(rol_administrador)

        db.session.commit()

        print(
            "[OK] El usuario administrador ya existe; "
            "se conserva su contraseña."
        )

        return

    admin_password = os.environ.get(
        "ADMIN_PASSWORD"
    )

    if not admin_password:
        raise RuntimeError(
            "La variable ADMIN_PASSWORD no está configurada."
        )

    usuario = Usuario(
        username=admin_username,
        nombre=admin_name
    )

    usuario.establecer_password(
        admin_password
    )
    rol_administrador = Rol.query.filter_by(nombre="Administrador").first()
    if rol_administrador:
        usuario.roles.append(rol_administrador)

    db.session.add(usuario)
    db.session.commit()

    print(
        "[OK] Usuario administrador creado correctamente."
    )


def cargar_contenidos():
    """
    Inserta los contenidos faltantes y actualiza los existentes.
    """

    nuevos = 0

    existentes = {
        contenido.slug: contenido
        for contenido in Contenido.query.all()
    }

    for datos in CONTENIDOS_INICIALES:
        contenido = existentes.get(datos["slug"])

        if contenido is not None:
            for campo, valor in datos.items():
                setattr(contenido, campo, valor)
            continue

        contenido = Contenido(**datos)

        db.session.add(contenido)

        nuevos += 1

    db.session.commit()

    print(
        f"[OK] Nuevos contenidos agregados: {nuevos}"
    )

    print(
        f"[OK] Total de contenidos: {Contenido.query.count()}"
    )


def cargar_pozos():
    """
    Inserta los pozos iniciales únicamente si aún no existen.
    """

    nuevos = 0

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

        if pozo is not None:
            for campo, valor in datos.items():
                setattr(pozo, campo, valor)
            continue

        pozo = Pozo(**datos)

        db.session.add(pozo)

        nuevos += 1

    db.session.commit()

    print(
        f"[OK] Nuevos pozos agregados: {nuevos}"
    )

    print(
        f"[OK] Total de pozos: {Pozo.query.count()}"
    )



def cargar_produccion_historica():
    """
    Inserta o actualiza la produccion historica mensual del Excel.
    """

    registros = leer_produccion_excel()

    if not registros:
        print("[AVISO] No se encontraron registros de produccion para cargar.")
        return

    existentes = {
        (registro.campo, registro.plataforma, registro.pozo, registro.fecha): registro
        for registro in ProduccionPozoMensual.query.all()
    }

    nuevos = 0

    for datos in registros:
        llave = (
            datos["campo"],
            datos["plataforma"],
            datos["pozo"],
            datos["fecha"],
        )
        registro = existentes.get(llave)

        if registro is None:
            db.session.add(ProduccionPozoMensual(**datos))
            nuevos += 1
            continue

        for campo, valor in datos.items():
            setattr(registro, campo, valor)

    db.session.commit()

    print(f"[OK] Nuevos registros de produccion: {nuevos}")
    print(
        "[OK] Total de registros de produccion: "
        f"{ProduccionPozoMensual.query.count()}"
    )


def inicializar_base_datos():
    """
    Inicializa completamente la base de datos.
    """

    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    with app.app_context():

        db.create_all()

        print(
            "\nInicializando base de datos...\n"
        )

        crear_usuario_administrador()

        cargar_contenidos()

        cargar_pozos()

        cargar_produccion_historica()

        print(
            "\n[OK] Base de datos lista.\n"
        )


if __name__ == "__main__":
    inicializar_base_datos()
