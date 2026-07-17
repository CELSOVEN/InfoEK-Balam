import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "clave-temporal-info-ek-balam"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'info_ek_balam.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "false"