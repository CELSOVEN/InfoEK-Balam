import os

from app import app
from database import db

from contenido_inicial import CONTENIDOS_INICIALES
from models import Usuario, Contenido


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

        print(
            "✓ El usuario administrador ya existe."
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
        "✓ Usuario administrador creado correctamente."
    )


def cargar_contenidos():
    """
    Inserta los contenidos iniciales únicamente
    si aún no existen.
    """

    nuevos = 0

    for datos in CONTENIDOS_INICIALES:

        existe = Contenido.query.filter_by(
            slug=datos["slug"]
        ).first()

        if existe:
            continue

        contenido = Contenido(**datos)

        db.session.add(contenido)

        nuevos += 1

    db.session.commit()

    print(
        f"✓ Nuevos contenidos agregados: {nuevos}"
    )

    print(
        f"✓ Total de contenidos: {Contenido.query.count()}"
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

        print(
            "\n✓ Base de datos lista.\n"
        )


if __name__ == "__main__":
    inicializar_base_datos()