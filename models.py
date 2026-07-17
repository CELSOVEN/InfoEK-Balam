from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    def establecer_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    @property
    def is_active(self):
        return self.activo


class Contenido(db.Model):
    __tablename__ = "contenidos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=False
    )

    resumen = db.Column(
        db.Text,
        nullable=True
    )

    contenido = db.Column(
        db.Text,
        nullable=False
    )

    palabras_clave = db.Column(
        db.Text,
        nullable=True
    )

    orden = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )