import os
from shiny import App, ui, render, reactive
from pathlib import Path

# Diccionario de Direcciones Zonales
dz_dict = {
    "01": "DZ-PIURA", "02": "DZ-LAMBAYEQUE", "03": "DZ-CAJAMARCA", "04": "DZ-LIMA",
    "05": "DZ-ICA", "06": "DZ-AREQUIPA", "07": "DZ-TACNA", "08": "DZ-LORETO",
    "09": "DZ-SAN MARTÍN", "10": "DZ-HUÁNUCO", "11": "DZ-JUNÍN", "12": "DZ-CUSCO", "13": "DZ-PUNO"
}

# Leer los meses desde los nombres de archivo en www/temp
def obtener_meses_disponibles():
    archivos = Path("www/temp").glob("out_*_*.png")
    yyyymm_set = set()
    for archivo in archivos:
        partes = archivo.stem.split("_")
        if len(partes) == 4:
            _, _, _, yyyymm = partes
            yyyymm_set.add(yyyymm)
    return {f"MES{i+1}": fecha for i, fecha in enumerate(sorted(yyyymm_set))}

meses_dict = obtener_meses_disponibles()

# UI
app_ui = ui.page_fluid(
    ui.h2("Pronóstico mensual por Dirección Zonal"),

    ui.row(
        ui.column(6, ui.input_select("dz_selected", "Dirección Zonal (DZ):", dz_dict)),
        ui.column(6, ui.input_select("mes_selected", "Mes del pronóstico:", meses_dict))
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
        yyyymm = meses_dict.get(mes_key, "")

        rutas = {
            "tmax": f"temp/out_mx2t24a_{dz_code}_{yyyymm}.png",
            "tmin": f"temp/out_mn2t24a_{dz_code}_{yyyymm}.png",
            "prec": f"temp/out_tpara_{dz_code}_{yyyymm}.png"
        }
        print("Rutas generadas:", rutas)
        return rutas

    def imagen_render(path_web, alt):
        path_disk = os.path.join("docs", path_web)  # Verificamos si existe el archivo físicamente
        if os.path.exists(path_disk):
            return {"src": path_web, "alt": alt, "style": "width: 100%;"}
        else:
            return None  # Evita error si no existe

    @output
    @render.image
    def img_tmax():
        return imagen_render(rutas_imagenes()["tmax"], "Tmax")

    @output
    @render.image
    def img_tmin():
        return imagen_render(rutas_imagenes()["tmin"], "Tmin")

    @output
    @render.image
    def img_prec():
        return imagen_render(rutas_imagenes()["prec"], "Precipitación")

# App
app = App(app_ui, server)
