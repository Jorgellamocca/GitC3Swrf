#Generados del dashboard interactivo
from shiny import App, ui, render, reactive
import os
import re

# Diccionario de Direcciones Zonales (clave = código)
dz_dict = {
    "01": "DZ-PIURA", "02": "DZ-LAMBAYEQUE", "03": "DZ-CAJAMARCA", "04": "DZ-LIMA",
    "05": "DZ-ICA", "06": "DZ-AREQUIPA", "07": "DZ-TACNA", "08": "DZ-LORETO",
    "09": "DZ-SAN MARTÍN", "10": "DZ-HUÁNUCO", "11": "DZ-JUNÍN", "12": "DZ-CUSCO", "13": "DZ-PUNO"
}

# Leer DZs disponibles desde los nombres de archivos
def obtener_dz_disponibles():
    archivos = os.listdir("temp") if os.path.exists("temp") else []
    dz_codigos = set()
    for f in archivos:
        match = re.search(r'_(\d{2})_\d{6}\.png$', f)
        if match:
            dz_codigos.add(match.group(1))
    dz_codigos = sorted(list(dz_codigos))
    return {dz: dz_dict.get(dz, f"DZ-{dz}") for dz in dz_codigos}

# Obtener los YYYYMM únicos disponibles y asignarles MES1 a MES6
def obtener_meses_disponibles():
    archivos = os.listdir("temp") if os.path.exists("temp") else []
    yyyymm_set = set()
    for f in archivos:
        match = re.search(r'_\d{2}_(\d{6})\.png$', f)
        if match:
            yyyymm_set.add(match.group(1))
    yyyymm_sorted = sorted(list(yyyymm_set))
    return {f"MES{i+1}": yyyymm for i, yyyymm in enumerate(yyyymm_sorted[:6])}

# UI
app_ui = ui.page_fluid(
    ui.h2("Pronóstico mensual por Dirección Zonal"),

    ui.row(
        ui.column(6, ui.input_select("dz_selected", "Dirección Zonal (DZ):", obtener_dz_disponibles())),
        ui.column(6, ui.input_select("mes_selected", "Mes del pronóstico:", obtener_meses_disponibles()))
    ),

    ui.h4("Pronóstico mensual: Tmax, Tmin y Precipitación"),
    ui.row(
        ui.column(4, ui.output_image("img_tmax")),
        ui.column(4, ui.output_image("img_tmin")),
        ui.column(4, ui.output_image("img_prec"))
    )
)

# Server
def server(input, output, session):

    @reactive.calc
    def rutas_imagenes():
        dz_code = input.dz_selected()
        mes_key = input.mes_selected()
        meses_dict = obtener_meses_disponibles()
        yyyymm = meses_dict.get(mes_key)

        if not dz_code or not yyyymm:
            return {"tmax": "", "tmin": "", "prec": ""}

        rutas = {
            "tmax": f"temp/out_mx2t24a_{dz_code}_{yyyymm}.png",
            "tmin": f"temp/out_mn2t24a_{dz_code}_{yyyymm}.png",
            "prec": f"temp/out_tpara_{dz_code}_{yyyymm}.png"
        }
        return rutas

    @output
    @render.image
    def img_tmax():
        ruta = rutas_imagenes()["tmax"]
        if os.path.exists(ruta):
            return {"src": ruta, "alt": "Tmax", "style": "width: 100%; max-width: 100%; height: auto;"}
        return {"src": "", "alt": "Imagen no encontrada"}

    @output
    @render.image
    def img_tmin():
        ruta = rutas_imagenes()["tmin"]
        if os.path.exists(ruta):
            return {"src": ruta, "alt": "Tmin", "style": "width: 100%; max-width: 100%; height: auto;"}
        return {"src": "", "alt": "Imagen no encontrada"}

    @output
    @render.image
    def img_prec():
        ruta = rutas_imagenes()["prec"]
        if os.path.exists(ruta):
            return {"src": ruta, "alt": "Precipitación", "style": "width: 100%; max-width: 100%; height: auto;"}
        return {"src": "", "alt": "Imagen no encontrada"}

# App
app = App(app_ui, server)
