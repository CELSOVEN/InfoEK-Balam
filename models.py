from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
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