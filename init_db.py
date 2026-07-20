import os

from app import app
from database import db

from contenido_inicial import CONTENIDOS_INICIALES
from datos_pozos import POZOS_INICIALES
from models import Usuario, Contenido, Pozo


def crear_usuario_administrador():
    """
    Crea el usuario administrador si aún no existe.
    """

    admin_username = os.environ.get(
        "ADMIN_USERNAME",
        "admin"
    )

    admin_password = os.environ.get(
        "ADMIN_PASSWORD"
    )

    admin_name = os.environ.get(
        "ADMIN_NAME",
        "Administrador"
    )

    if not admin_password:
        raise RuntimeError(
            "La variable ADMIN_PASSWORD no está configurada."
        )

    usuario = Usuario.query.filter_by(
        username=admin_username
    ).first()

    if usuario:

        usuario.establecer_password(admin_password)

        db.session.commit()

        print(
            "[OK] Contraseña del administrador actualizada."
        )

        return

    usuario = Usuario(
        username=admin_username,
        nombre=admin_name
    )

    usuario.establecer_password(
        admin_password
    )

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

        print(
            "\n[OK] Base de datos lista.\n"
        )


if __name__ == "__main__":
    inicializar_base_datos()
