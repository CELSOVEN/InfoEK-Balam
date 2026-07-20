"""Carga los datos maestros desde ``data/platforms_wells2.xlsx``.

Se usa únicamente la biblioteca estándar para no añadir una dependencia de
lectura de Excel al despliegue de la aplicación.
"""

from datetime import datetime, timedelta
from pathlib import Path
import re
from xml.etree import ElementTree
from zipfile import ZipFile


ARCHIVO_POZOS = Path(__file__).parent / "data" / "platforms_wells2.xlsx"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _indice_columna(referencia):
    letras = re.match(r"[A-Z]+", referencia).group()
    indice = 0
    for letra in letras:
        indice = indice * 26 + ord(letra) - ord("A") + 1
    return indice - 1


def _fecha_excel(valor):
    if not valor:
        return ""
    try:
        fecha = datetime(1899, 12, 30) + timedelta(days=float(valor))
    except (TypeError, ValueError):
        return str(valor)
    return fecha.strftime("%d-%b-%Y")


def _numero(valor):
    if not valor:
        return ""
    try:
        return f"{float(valor):.10g}"
    except (TypeError, ValueError):
        return str(valor).strip()


def _leer_filas():
    with ZipFile(ARCHIVO_POZOS) as libro:
        compartidas = []
        if "xl/sharedStrings.xml" in libro.namelist():
            raiz = ElementTree.fromstring(libro.read("xl/sharedStrings.xml"))
            compartidas = [
                "".join(texto.text or "" for texto in elemento.iter(f"{{{NS}}}t"))
                for elemento in raiz
            ]

        hoja = ElementTree.fromstring(libro.read("xl/worksheets/sheet1.xml"))
        filas = hoja.findall(f".//{{{NS}}}sheetData/{{{NS}}}row")[3:]

        for fila in filas:
            valores = [""] * 16
            for celda in fila.findall(f"{{{NS}}}c"):
                indice = _indice_columna(celda.attrib["r"])
                if indice >= len(valores):
                    continue
                nodo_valor = celda.find(f"{{{NS}}}v")
                valor = "" if nodo_valor is None else nodo_valor.text
                if celda.attrib.get("t") == "s" and valor:
                    valor = compartidas[int(valor)]
                valores[indice] = valor
            yield valores[1:16]


def _crear_registro(fila):
    (elemento, plataforma, fecha_instalacion, tipo, servicio,
     profundidad_agua, numero_pozos, pozos, coordenada_x, coordenada_y,
     tipo_perforacion, inicio_perforacion, fin_perforacion,
     profundidad_total, profundidad_vertical) = fila

    elemento = elemento.strip()
    plataforma = plataforma.strip()
    pozos = pozos.strip()
    es_centro = elemento.casefold() == "center of structure"
    nombre = elemento or f"{plataforma} ({servicio or 'registro'})"
    if es_centro:
        # ``nombre`` era único en las primeras versiones de la base de datos.
        nombre = f"Center of Structure - {plataforma}"

    coordenadas = " / ".join(
        valor for valor in (_numero(coordenada_x), _numero(coordenada_y)) if valor
    )
    try:
        cantidad = int(float(numero_pozos)) if numero_pozos else None
    except ValueError:
        cantidad = None

    datos = {
        "nombre": nombre,
        "elemento": elemento,
        "plataforma": plataforma,
        "fecha_instalacion": fecha_instalacion.strip(),
        "tipo": tipo.strip(),
        "servicio": servicio.strip(),
        "profundidad_agua": _numero(profundidad_agua),
        "numero_pozos": cantidad,
        "pozos": pozos,
        "coordenadas_utm": coordenadas,
        "tipo_perforacion": tipo_perforacion.strip(),
        "inicio_perforacion": _fecha_excel(inicio_perforacion),
        "fin_perforacion": _fecha_excel(fin_perforacion),
        "profundidad_total": _numero(profundidad_total),
        "profundidad_vertical": _numero(profundidad_vertical),
    }
    datos["palabras_clave"] = " ".join(
        str(valor) for valor in (
            elemento, pozos, plataforma, fecha_instalacion, tipo, servicio,
            tipo_perforacion, "centro estructura" if es_centro else "pozos plataforma",
        ) if valor
    )
    datos["activo"] = True
    return datos


POZOS_INICIALES = [_crear_registro(fila) for fila in _leer_filas()]
