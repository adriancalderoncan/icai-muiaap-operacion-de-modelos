# Practica AEMET - Requests

## Entorno

```
python -m venv venv
source venv/Scripts/activate
pip install requests
```

En Linux o Mac se activa con source venv/bin/activate.

## API key

La API key se pide en la web de AEMET OpenData y llega por correo. La guardo en una variable de entorno para no subirla al repositorio:

```
export AEMET_API_KEY=mi_api_key
```

## Ejecutar

```
python aemet.py
```

## Que hace aemet.py

1. Llama al inventario de estaciones pasando la api_key como query string.
2. AEMET no devuelve los datos directamente. Devuelve un JSON con un enlace en "datos", asi que hago una segunda peticion a ese enlace.
3. Busco la estacion "MADRID, CIUDAD UNIVERSITARIA" y me quedo con su indicativo (idema).
4. Llamo a climatologias diarias con fechaIniStr 2019-10-01T00:00:00UTC, fechaFinStr 2019-10-30T23:59:59UTC y el idema.
5. Hago otra vez la segunda peticion al enlace de "datos" y saco por pantalla la fecha, la temperatura media, la maxima, la minima y la precipitacion de cada dia.
