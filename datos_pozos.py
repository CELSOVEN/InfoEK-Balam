"""Datos maestros de pozos tomados de data/platforms_wells.xlsx."""


_COLUMNAS = (
    "nombre", "plataforma", "fecha_instalacion", "tipo", "servicio",
    "profundidad_agua", "numero_pozos", "pozos", "coordenadas_utm",
    "tipo_perforacion", "inicio_perforacion", "fin_perforacion",
    "profundidad_total", "profundidad_vertical",
)


_POZOS = (
    ('Well Balam-2 DES (Development)', 'Balam-TA', '2021', 'Tripod', 'Drilling', '48', 1, 'Balam-2', '608503.24 / 2155272.43', '', '27-Apr-2021', '30-Aug-2021', '5119', '4457'),
    ('Well Balam-22 DES (Development)', 'Balam-TA', '2021', 'Tripod', 'Drilling', '48', 1, 'Balam-22', '608502.79 / 2155274.62', 'Directional', '10-Jan-2020', '18-Mar-2020', '5140', ''),
    ('Well Balam-47 DES (Development)', 'Balam-TB', '2017', 'Tetrapod', 'Drilling', '47.9', 1, 'Balam-47', '609958.52 / 2154718.62', 'Horizontal', '12-May-2018', '10-Aug-2018', '5149', '4430'),
    ('Well Balam-63 DES (Development)', 'Balam-TB', '2017', 'Tetrapod', 'Drilling', '47.9', 1, 'Balam-63', '609960.77 / 2154720.86', 'Directional', '27-Oct-2018', '23-Jan-2019', '4621', '4508'),
    ('Well Balam-67 DES (Development)', 'Balam-TB', '2017', 'Tetrapod', 'Drilling', '47.9', 1, 'Balam-67', '609958.43 / 2154722.85', 'Directional', '26-Feb-2019', '26-May-2019', '5340', '4835'),
    ('Well Balam-69 INY (Water Injector)', 'Balam-TB', '2017', 'Tetrapod', 'Drilling', '47.9', 1, 'Balam-69', '609958.74 / 2154722.41', 'Directional', '28-Jan-2020', '26-Apr-2020', '5296', '4532'),
    ('Well Balam 3 DES (Development)', 'Balam-TD', '2005', 'Tetrapod', 'Drilling', '50.3', 1, 'Balam-3', '608111.64 / 2157265.3', 'Directional', '25-Sep-2018', '18-Dec-2018', '5386', '4418'),
    ('Well Balam 71 (Development)', 'Balam-TE', '2020', 'Tetrapod', 'Drilling', '51.2', 1, 'Balam-71', '606837.62 / 2158075.94', 'Directional', '26-Jul-1993', '14-Feb-1994', '3643', '3379'),
    ('Well Balam 75', 'Balam-TE', '2020', 'Tetrapod', 'Drilling', '51.2', 1, 'Balam-75', '606842.85 / 2158072.56', 'Directional', '21-Aug-2013', '02-Aug-2014', '4845', '4476'),
    ('Well Balam 91 (Development)', 'Balam-TE', '2020', 'Tetrapod', 'Drilling', '51.2', 1, 'Balam-91', '606843.03 / 2158075.6', 'Deviated', '05-Mar-1993', '10-Jul-1993', '4611', '4572'),
    ('Well Ek 35H', 'Balam-TE', '2020', 'Tetrapod', 'Drilling', '51.2', 1, 'Ek-35H', '606837.31 / 2158072.97', 'Horizontal', '23-Aug-2009', '07-Nov-2009', '3497', '3004'),
    ('Well Ek 55 (Development)', 'Balam-TE', '2020', 'Tetrapod', 'Drilling', '51.2', 1, 'Ek-55', '606840.39 / 2158075.74', 'Deviated', '31-Dec-2008', '26-Mar-2009', '3707', '3081.3'),
    ('Well Balam-32 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-32', '610021.61 / 2154592.48', '', '14-Jul-2022', '25-Nov-2022', '5174', '4512'),
    ('Well Balam-41 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-41', '610025.68 / 2154593.15', 'Directional', '01-Mar-2023', '04-Jun-2023', '4900', '4594'),
    ('Well Balam-42 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-42', '610023.72 / 2154590.75', 'Directional J', '26-Jun-2019', '23-Nov-2019', '5302', '4983'),
    ('Well Balam-61 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-61', '610031.71 / 2154596.23', '', '22-Nov-2020', '09-Apr-2021', '5101', '4483'),
    ('Well Balam-85 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-85', '610025.84 / 2154589.02', 'Directional', '13-Mar-2020', '16-Sep-2020', '5034', '4681'),
    ('Well Balam-93 DES (Development)', 'Balam-A', '2014', 'Octapod', 'Drilling', '47.9', 1, 'Balam-93', '610029.6 / 2154597.95', '', '01-Dec-2021', '09-Mar-2022', '4826', '4463'),
    ('Well Balam-5 DES (Development)', 'Balam-TA2', '2022', 'Tetrapod (Lightweight Marine Structure)', 'Drilling', '47.9', 1, 'Balam-5', '610095.67 / 2154572.8', '', '01-Aug-2022', '03-Oct-2022', '5660', '4577'),
    ('Well Balam-87 DES (Development)', 'Balam-TA2', '2022', 'Tetrapod (Lightweight Marine Structure)', 'Drilling', '47.9', 1, 'Balam-87', '610095.78 / 2154568.78', '', '16-Feb-2023', '30-Apr-2023', '5180', '4480'),
    ('Well Ek-11', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-11', '604923.39 / 2157269.98', 'Deviated', '14-May-1993', '01-Aug-1993', '4874', '4671'),
    ('Well Ek-27 DES (Development)', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-27', '604925.31 / 2157268.05', '--', '02-Jul-2022', '13-Oct-2022', '5035', '4223'),
    ('Well Ek-31', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-31', '604921.94 / 2157267.79', 'Deviated', '03-Apr-1991', '03-Dec-1991', '5158', '4755'),
    ('Well Ek-33', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-33', '604922.86 / 2157261.75', 'Deviated', '17-Mar-1994', '15-Aug-1994', '4884', '4632'),
    ('Well Ek-56', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-56', '604916.81 / 2157263.41', 'Directional', '27-Jul-2012', '08-Oct-2012', '3133', '2981'),
    ('Well Ek-101', 'Ek-A', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-101', '604918.74 / 2157261.48', 'Vertical', '01-Mar-1990', '17-Jan-1991', '4607', '4607'),
    ('Well Ek-14 DES (Development)', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-14', '604786.25 / 2157348.57', '', '14-Mar-2021', '20-May-2021', '5110', '4225'),
    ('Well Ek-29 DES (Development)', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-29', '604783.98 / 2157350.07', '', '07-Jul-2022', '30-Sep-2022', '5443', '4608'),
    ('Well Ek-32 DES (Development)', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-32', '604785.15 / 2157356.74', 'Directional J', '09-Aug-2019', '22-Dec-2019', '4680', '4565'),
    ('Well Ek-47 DES', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-47', '604787.42 / 2157355.23', '', '28-Jun-2020', '18-Sep-2020', '5066', '4255'),
    ('Well Ek-53 DES', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-53', '604789.69 / 2157353.73', 'Directional J', '08-Dec-2021', '07-Feb-2022', '4467', '4264'),
    ('Well Ek-57 DES (Development)', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-57', '604782.27 / 2157347.5', '', '04-May-2023', '10-Jul-2023', '5403', '4725'),
    ('Well Ek-69 DES (Development)', 'Ek-A2', '2018', 'Octapod', 'Drilling', '51', 1, 'Ek-69', '604785.7 / 2157352.65', '', '12-Nov-2022', '31-Mar-2023', '5667', '4654'),
    ('Well Ek-9', 'Ek-TA', '1996', 'Tripod', 'Drilling', '49.9', 1, 'Ek-9', '606154.49 / 2156605.43', '--', '02-Apr-2014', '12-May-2015', '--', '--'),
    ('Well Ek-17 DES (Development)', 'Ek-TA', '1996', 'Tripod', 'Drilling', '49.9', 1, 'Ek-17', '606155.18 / 2156603.29', 'Horizontal', '07-Dec-2018', '30-Apr-2019', '4912', '4416'),
    ('Well Ek-21', 'Ek-TA', '1996', 'Tripod', 'Drilling', '49.9', 1, 'Ek-21', '606151.86 / 2156604.27', 'Directional', '28-May-1993', '26-Jul-1993', '4852', '4699'),
    ('Well Ek-25', 'Ek-TA', '1996', 'Tripod', 'Drilling', '49.9', 1, 'Ek-25', '606154.35 / 2156603.51', 'Directional', '30-Jan-1994', '11-Apr-1994', '4380', '4298'),
    ('Well Ek-37 DES (Development)', 'Ek-TA', '1996', 'Tripod', 'Drilling', '49.9', 1, 'Ek-37', '606152.83 / 2156605.04', 'Directional J', '29-Jul-2019', '20-Oct-2019', '4520', '4261'),
    ('Well Ek-41 (Development)', 'Ek-TB', '1996', 'Tripod', 'Drilling', '49.1', 1, 'Ek-41', '607328.19 / 2155850.28', '', '10-Nov-2013', '18-Feb-2014', '', ''),
    ('Well Ek 63 DES (Development)', 'Ek-TB', '1996', 'Tripod', 'Drilling', '49.1', 1, 'Ek-63', '607325.84 / 2155852.03', 'Deviated', '11-Apr-1993', '17-Jul-1993', '4937', '4790'),
)


def _crear_registro(fila):
    datos = dict(zip(_COLUMNAS, fila))
    datos["palabras_clave"] = " ".join(
        valor for valor in (
            datos["pozos"], datos["plataforma"], datos["fecha_instalacion"],
            datos["tipo"], datos["servicio"], datos["tipo_perforacion"],
            "pozos plataforma",
        ) if valor
    )
    datos["activo"] = True
    return datos


POZOS_INICIALES = [_crear_registro(fila) for fila in _POZOS]
