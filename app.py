import os
import sys
from shiny import App, ui, render, reactive

# Detecta si estamos en Pyodide (navegador con Shinylive)
IS_LOCAL = not ("pyodide" in sys.modules)

# Diccionario de Direcciones Zonales (DZ)
dz_dict = {
    "01": "DZ-PIURA", "02": "DZ-LAMBAYEQUE", "03": "DZ-CAJAMARCA", "04": "DZ-LIMA",
    "05": "DZ-ICA", "06": "DZ-AREQUIPA", "07": "DZ-TACNA", "08": "DZ-LORETO",
    "09": "DZ-SAN MARTÍN", "10": "DZ-HUÁNUCO", "11": "DZ-JUNÍN", "12": "DZ-CUSCO", "13": "DZ-PUNO"
}

# Meses fijos, porque en Shinylive no se puede escanear el sistema de archivos
meses_dict = {
    "MES1": "202504",
    "MES2": "202505",
    "MES3": "202506",
    "MES4": "202507",
    "MES5": "202508",
    "MES6": "202509"
}

# Interfaz
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

# Servidor
def server(input, output, session):

    @reactive.calc
    def rutas_imagenes():
        dz_code = input.dz_selected()
        mes_key = input.mes_selected()
        yyyymm = meses_dict.get(mes_key, "")

        return {
            "tmax": f"temp/out_mx2t24a_{dz_code}_{yyyymm}.png",
            "tmin": f"temp/out_mn2t24a_{dz_code}_{yyyymm}.png",
            "prec": f"temp/out_tpara_{dz_code}_{yyyymm}.png"
        }

    def imagen_render(path_web, alt):
        # Validación solo en local
        if IS_LOCAL:
            path_disk = os.path.join("docs/temp", os.path.basename(path_web))
            if os.path.exists(path_disk):
                return {"src": path_web, "alt": alt, "style": "width: 100%;"}
            else:
                return {
                    "src": "https://via.placeholder.com/400x300?text=No+disponible",
                    "alt": f"{alt} no disponible",
                    "style": "width: 100%;"
                }
        else:
            # En Shinylive no se puede validar existencia de archivos
            return {"src": path_web, "alt": alt, "style": "width: 100%;"}

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
