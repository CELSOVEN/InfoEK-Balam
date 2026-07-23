from pathlib import Path

from datos_produccion import leer_produccion_excel


def test_leer_produccion_excel_ayatsil():
    ruta = Path("data/P535 - PRODUCCION AYATSIL.xlsx")

    registros = leer_produccion_excel(ruta)

    assert registros, "No se cargaron registros desde el Excel de Ayatsil"
    assert any(
        registro["campo"] == "AYATSIL-TEKEL"
        and registro["plataforma"] == "AYATSIL-A"
        and registro["pozo"] == "AYATSIL-4 DES"
        for registro in registros
    )
