##Generados de las imagenes mensuales
#sALIDAS out_variable_DZ_YYYYMM.png:
import os
import requests
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
from matplotlib.colors import BoundaryNorm
from scipy.interpolate import griddata
import matplotlib.ticker as mticker
import pandas as pd

# Diccionario de Direcciones Zonales
dz_dict = {
    "01": "DZ-PIURA", "02": "DZ-LAMBAYEQUE", "03": "DZ-CAJAMARCA", "04": "DZ-LIMA",
    "05": "DZ-ICA", "06": "DZ-AREQUIPA", "07": "DZ-TACNA", "08": "DZ-LORETO",
    "09": "DZ-SAN MARTÍN", "10": "DZ-HUÁNUCO", "11": "DZ-JUNÍN", "12": "DZ-CUSCO", "13": "DZ-PUNO"
}

# -------------------------- DESCARGA --------------------------
def download_file(url, local_path):
    if not os.path.exists(local_path):
        r = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(r.content)
        print(f"Descargado: {local_path}")

# Shapefiles y NetCDF
download_file("https://raw.githubusercontent.com/Jorgellamocca/GitC3Swrf/main/shape/DIRECCIONES_ZONALES.shp", "departamentos.shp")
download_file("https://raw.githubusercontent.com/Jorgellamocca/GitC3Swrf/main/shape/DIRECCIONES_ZONALES.dbf", "departamentos.dbf")
download_file("https://raw.githubusercontent.com/Jorgellamocca/GitC3Swrf/main/shape/DIRECCIONES_ZONALES.shx", "departamentos.shx")
download_file("https://raw.githubusercontent.com/Jorgellamocca/GitC3Swrf/main/data/flx.anom.ecmwf.nc", "flx.anom.ecmwf.nc")

os.makedirs("temp", exist_ok=True)

# -------------------------- CARGA --------------------------
gdf = gpd.read_file("departamentos.shp")
gdf['DZ'] = gdf['DZ'].astype(str).str.zfill(2)

ds = xr.open_dataset("flx.anom.ecmwf.nc")
ref_time = pd.to_datetime(ds['forecast_reference_time'].values[0])

if 'tpara' in ds:
    ds['tpara'] = ds['tpara'] * 1000 * 30 * 24 * 3600

forecast_months = ds['forecastMonth'].values
fechas_pronostico = [ref_time + pd.DateOffset(months=int(m - 1)) for m in forecast_months]

# -------------------------- CONFIG VARS --------------------------
variables_info = {
    'mx2t24a': {
        'cmap': 'coolwarm',
        'bounds': np.array([-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]),
        'titulo': 'Anomalía de Tmax', 'label': 'Tmax (°C)'
    },
    'mn2t24a': {
        'cmap': 'coolwarm',
        'bounds': np.array([-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]),
        'titulo': 'Anomalía de Tmin', 'label': 'Tmin (°C)'
    },
    'tpara': {
        'cmap': 'BrBG',
        'bounds': np.array([-100, -80, -50, -30, -20, -10, 0, 10, 20, 30, 50, 80, 100]),
        'titulo': 'Anomalía de Precip', 'label': 'Prec (mm/mes)'
    }
}

# -------------------------- INTERPOLACIÓN --------------------------
def cubic_interpolation(variable, lon, lat, new_lon, new_lat):
    lon2d, lat2d = np.meshgrid(lon, lat)
    points = np.array([lon2d.flatten(), lat2d.flatten()]).T
    values = variable.values.flatten()
    new_lon2d, new_lat2d = np.meshgrid(new_lon, new_lat)
    new_points = np.array([new_lon2d.flatten(), new_lat2d.flatten()]).T
    interp = griddata(points, values, new_points, method='cubic')
    return interp.reshape(new_lon2d.shape)

# -------------------------- GENERACIÓN --------------------------
for dz_code in dz_dict:
    gdf_sel = gdf[gdf['DZ'] == dz_code]
    if gdf_sel.empty:
        continue
    extent = gdf_sel.total_bounds

    for var_name, info in variables_info.items():
        if var_name not in ds:
            continue
        for i, fecha in enumerate(fechas_pronostico):
            v = ds[var_name].sel(forecastMonth=i + 1)
            lon = v['longitude'].values
            lat = v['latitude'].values
            new_lon = np.linspace(lon.min(), lon.max(), 200)
            new_lat = np.linspace(lat.min(), lat.max(), 200)
            interp = cubic_interpolation(v, lon, lat, new_lon, new_lat)

            fig, ax = plt.subplots(figsize=(7, 6), subplot_kw={'projection': ccrs.PlateCarree()})
            norm = BoundaryNorm(info['bounds'], ncolors=256)
            im = ax.contourf(new_lon, new_lat, interp, levels=info['bounds'],
                             cmap=info['cmap'], norm=norm, extend='both')
            gdf_sel.boundary.plot(ax=ax, edgecolor='black', linewidth=0.8)
            ax.set_extent([extent[0], extent[2], extent[1], extent[3]])
            ax.set_title(f"{info['titulo']} - {dz_dict[dz_code]}\n{fecha.strftime('%b-%Y').upper()}", fontsize=11)

            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False

            cbar = fig.colorbar(im, ax=ax, shrink=0.7)
            cbar.set_label(info['label'])

            fname = f"temp/out_{var_name}_{dz_code}_{fecha.strftime('%Y%m')}.png"
            plt.savefig(fname, dpi=150, bbox_inches="tight")
            plt.close()
