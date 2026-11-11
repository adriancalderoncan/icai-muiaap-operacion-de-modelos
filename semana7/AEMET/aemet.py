import os

import requests

API_KEY = os.environ["AEMET_API_KEY"]
BASE_URL = "https://opendata.aemet.es/opendata/api"


def pedir_datos(url):
    respuesta = requests.get(url, params={"api_key": API_KEY}, timeout=30)
    print(url, respuesta.status_code)
    respuesta.raise_for_status()
    enlace = respuesta.json()["datos"]
    datos = requests.get(enlace, timeout=30)
    datos.raise_for_status()
    datos.encoding = "latin-1"
    return datos.json()


estaciones = pedir_datos(
    BASE_URL + "/valores/climatologicos/inventarioestaciones/todasestaciones"
)

idema = None
for estacion in estaciones:
    if estacion["nombre"] == "MADRID, CIUDAD UNIVERSITARIA":
        idema = estacion["indicativo"]
print("Indicativo:", idema)

fecha_ini = "2019-10-01T00:00:00UTC"
fecha_fin = "2019-10-30T23:59:59UTC"
climatologia = pedir_datos(
    BASE_URL
    + "/valores/climatologicos/diarios/datos/fechaini/"
    + fecha_ini
    + "/fechafin/"
    + fecha_fin
    + "/estacion/"
    + idema
)

for dia in climatologia:
    print(dia["fecha"], dia.get("tmed"), dia.get("tmax"), dia.get("tmin"), dia.get("prec"))
