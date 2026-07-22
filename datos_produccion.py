"""Carga la produccion historica mensual desde el Excel de data."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_PRODUCCION = (
    BASE_DIR / "data" / "P535 - PRODUCCION (CONJUNTO DE PLATAFORMAS).xlsx"
)
HOJA_PRODUCCION = "PRODUCCION"
FILA_ENCABEZADO = 7

COLUMNAS_PRODUCCION = {
    "campo",
    "plataforma",
    "pozo",
    "fecha",
    "gas_mmpcd",
    "agua_mbd",
    "aceite_mbd",
    "gor_pc_bbl",
}


def normalizar_texto(valor: Any) -> str:
    return str(valor or "").strip()


def normalizar_columna(valor: Any) -> str:
    texto = normalizar_texto(valor).replace("\n", " ").lower()
    texto = " ".join(texto.split())
    equivalencias = {
        "campo": "campo",
        "plataforma": "plataforma",
        "pozo": "pozo",
        "gas mmpcd": "gas_mmpcd",
        "agua mbd": "agua_mbd",
        "aceite mbd": "aceite_mbd",
        "goc pc/bbl": "gor_pc_bbl",
        "gor pc/bbl": "gor_pc_bbl",
        "fecha": "fecha",
    }
    return equivalencias.get(texto, texto)


def normalizar_fecha(valor: Any) -> date | None:
    if isinstance(valor, datetime):
        return date(valor.year, valor.month, 1)
    if isinstance(valor, date):
        return date(valor.year, valor.month, 1)
    if not valor:
        return None

    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            fecha = datetime.strptime(str(valor).strip(), formato)
            return date(fecha.year, fecha.month, 1)
        except ValueError:
            continue
    return None


def normalizar_numero(valor: Any) -> float:
    if valor in (None, ""):
        return 0.0
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def leer_produccion_excel(
    ruta_excel: Path = ARCHIVO_PRODUCCION,
) -> list[dict[str, Any]]:
    """Lee el Excel de produccion y devuelve registros normalizados."""
    if not ruta_excel.exists():
        return []

    libro = load_workbook(ruta_excel, read_only=True, data_only=True)
    hoja = libro[libro.sheetnames[0]]
    for nombre_hoja in libro.sheetnames:
        nombre_normalizado = normalizar_texto(nombre_hoja).upper().replace("Ó", "O")
        if nombre_normalizado == HOJA_PRODUCCION:
            hoja = libro[nombre_hoja]
            break

    encabezados = [
        normalizar_columna(celda.value)
        for celda in hoja[FILA_ENCABEZADO]
    ]
    posiciones = {
        nombre: indice
        for indice, nombre in enumerate(encabezados)
        if nombre in COLUMNAS_PRODUCCION
    }

    faltantes = COLUMNAS_PRODUCCION.difference(posiciones)
    if faltantes:
        raise RuntimeError(
            "El Excel de produccion no tiene columnas requeridas: "
            + ", ".join(sorted(faltantes))
        )

    registros: dict[tuple[str, str, str, date], dict[str, Any]] = {}

    for fila in hoja.iter_rows(min_row=FILA_ENCABEZADO + 1, values_only=True):
        campo = normalizar_texto(fila[posiciones["campo"]]).upper()
        plataforma = normalizar_texto(fila[posiciones["plataforma"]]).upper()
        pozo = normalizar_texto(fila[posiciones["pozo"]]).upper()
        fecha = normalizar_fecha(fila[posiciones["fecha"]])

        if not campo or not plataforma or not pozo or fecha is None:
            continue

        llave = (campo, plataforma, pozo, fecha)
        registro = {
            "campo": campo,
            "plataforma": plataforma,
            "pozo": pozo,
            "fecha": fecha,
            "gas_mmpcd": normalizar_numero(fila[posiciones["gas_mmpcd"]]),
            "agua_mbd": normalizar_numero(fila[posiciones["agua_mbd"]]),
            "aceite_mbd": normalizar_numero(fila[posiciones["aceite_mbd"]]),
            "gor_pc_bbl": normalizar_numero(fila[posiciones["gor_pc_bbl"]]),
        }

        if llave not in registros:
            registros[llave] = registro
            continue

        registros[llave]["gas_mmpcd"] += registro["gas_mmpcd"]
        registros[llave]["agua_mbd"] += registro["agua_mbd"]
        registros[llave]["aceite_mbd"] += registro["aceite_mbd"]
        registros[llave]["gor_pc_bbl"] = registro["gor_pc_bbl"]

    return sorted(
        registros.values(),
        key=lambda item: (
            item["campo"],
            item["plataforma"],
            item["pozo"],
            item["fecha"],
        ),
    )
