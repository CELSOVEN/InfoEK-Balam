import os

from app import app
from database import db
from models import Usuario


def inicializar_base_datos():
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        db.create_all()

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

        usuario_existente = Usuario.query.filter_by(
            username=admin_username
        ).first()

        if usuario_existente:
            print("El usuario administrador ya existe.")
            return

        usuario = Usuario(
            username=admin_username,
            nombre=admin_name
        )

        usuario.establecer_password(admin_password)

        db.session.add(usuario)
        db.session.commit()

        print("Base de datos inicializada correctamente.")
        print(f"Usuario administrador: {admin_username}")


if __name__ == "__main__":
    inicializar_base_datos()