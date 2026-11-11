# Respuestas microejercicios HTTP y JSON

## 1. Tres formas de pedir una prediccion

- A: no sale del proceso, no usa HTTP, es una llamada a una funcion, no hay ruta.
- B: si sale del proceso, si usa HTTP, la ruta nombra una accion (runPumpModel).
- C: si sale del proceso, si usa HTTP, la ruta nombra un recurso (predictions).

## 2. URL, path y query

http://127.0.0.1:8000/v1/predictions/pred-42?include=explanation&limit=1

- scheme: http
- host: 127.0.0.1
- port: 8000
- path: /v1/predictions/pred-42
- query: include=explanation y limit=1

Donde pondria cada cosa:

- el id de una prediccion: en el path, /v1/predictions/pred-42
- un limite de resultados: en la query, ?limit=1
- cuatro medidas de una bomba: en el body JSON, no en la URL

## 3. JSON y Python

```json
{"machine_id": "pump-017", "ready": true, "comment": null, "axes": [1, 2]}
```

True pasa a true, None pasa a null y la tupla pasa a una lista. Lo he comprobado con json.loads y lo lee sin error.

## 4. Cuatro estados HTTP

1. Codigo 200, la peticion ha ido bien y se devuelve la prediccion.
2. Codigo 400, el servidor no puede leer el cuerpo porque no es JSON.
3. Codigo 422, el JSON se lee bien pero vibration_mm_s tiene que ser un numero.
4. Codigo 503, la peticion esta bien pero el servicio no esta disponible ahora.

## 5. Crear y consultar una prediccion

```text
Crear una prediccion:    POST /v1/predictions
Consultar la prediccion: GET /v1/predictions/pred-42
```

- Las mediciones van en el body JSON.
- pred-42 va en el path.
- Si se repite dos veces la creacion se crean dos predicciones distintas.
- Consultar dos veces no cambia nada en el servidor.

Crear (POST) no es segura porque cambia el estado del servidor, y no es idempotente porque repetirla crea otra prediccion. Consultar (GET) es segura porque solo lee, y es idempotente porque repetirla da el mismo efecto.
