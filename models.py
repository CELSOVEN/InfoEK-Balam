from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


roles_permisos = db.Table(
    "roles_permisos",
    db.Column("rol_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column(
        "permiso_id",
        db.Integer,
        db.ForeignKey("permisos.id"),
        primary_key=True,
    ),
)

usuarios_roles = db.Table(
    "usuarios_roles",
    db.Column(
        "usuario_id",
        db.Integer,
        db.ForeignKey("usuarios.id"),
        primary_key=True,
    ),
    db.Column("rol_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class Permiso(db.Model):
    __tablename__ = "permisos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)


class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    es_sistema = db.Column(db.Boolean, default=False, nullable=False)
    permisos = db.relationship(
        "Permiso",
        secondary=roles_permisos,
        lazy="selectin",
        backref=db.backref("roles", lazy="selectin"),
    )


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

    roles = db.relationship(
        "Rol",
        secondary=usuarios_roles,
        lazy="selectin",
        backref=db.backref("usuarios", lazy="selectin"),
    )

    sesiones_navegacion = db.relationship(
        "SesionNavegacion",
        back_populates="usuario",
        lazy="dynamic",
    )

    def establecer_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def tiene_permiso(self, codigo):
        return any(
            permiso.codigo == codigo
            for rol in self.roles
            for permiso in rol.permisos
        )

    @property
    def is_active(self):
        return self.activo


class SesionNavegacion(db.Model):
    __tablename__ = "sesiones_navegacion"
    __table_args__ = (
        db.Index(
            "ix_sesiones_navegacion_usuario_ingreso",
            "usuario_id",
            "fecha_ingreso",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
    )
    fecha_ingreso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ultima_actividad = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    usuario = db.relationship("Usuario", back_populates="sesiones_navegacion")

    @property
    def duracion_segundos(self):
        fin = self.fecha_salida or self.ultima_actividad
        return max(0, int((fin - self.fecha_ingreso).total_seconds()))


class Pozo(db.Model):
    __tablename__ = "pozos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(250),
        unique=True,
        nullable=False
    )

    elemento = db.Column(
        db.String(250),
        nullable=True
    )

    plataforma = db.Column(
        db.String(100),
        nullable=True
    )

    fecha_instalacion = db.Column(
        db.String(50),
        nullable=True
    )

    tipo = db.Column(
        db.String(100),
        nullable=True
    )

    servicio = db.Column(
        db.String(100),
        nullable=True
    )

    profundidad_agua = db.Column(
        db.String(50),
        nullable=True
    )

    numero_pozos = db.Column(
        db.Integer,
        nullable=True
    )

    pozos = db.Column(
        db.String(200),
        nullable=True
    )

    coordenadas_utm = db.Column(
        db.String(120),
        nullable=True
    )

    tipo_perforacion = db.Column(
        db.String(100),
        nullable=True
    )

    inicio_perforacion = db.Column(
        db.String(50),
        nullable=True
    )

    fin_perforacion = db.Column(
        db.String(50),
        nullable=True
    )

    profundidad_total = db.Column(
        db.String(50),
        nullable=True
    )

    profundidad_vertical = db.Column(
        db.String(50),
        nullable=True
    )

    palabras_clave = db.Column(
        db.Text,
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

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



class ProduccionPozoMensual(db.Model):
    __tablename__ = "produccion_pozo_mensual"
    __table_args__ = (
        db.UniqueConstraint(
            "campo",
            "plataforma",
            "pozo",
            "fecha",
            name="uq_produccion_pozo_fecha",
        ),
        db.Index(
            "ix_produccion_fecha_campo",
            "fecha",
            "campo",
            "plataforma",
            "pozo",
        ),
        db.Index("ix_produccion_pozo_fecha", "pozo", "fecha"),
    )

    id = db.Column(db.Integer, primary_key=True)
    campo = db.Column(db.String(20), nullable=False)
    plataforma = db.Column(db.String(50), nullable=False)
    pozo = db.Column(db.String(80), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    gas_mmpcd = db.Column(db.Float, nullable=False, default=0)
    agua_mbd = db.Column(db.Float, nullable=False, default=0)
    aceite_mbd = db.Column(db.Float, nullable=False, default=0)
    gor_pc_bbl = db.Column(db.Float, nullable=False, default=0)
    fecha_carga = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
