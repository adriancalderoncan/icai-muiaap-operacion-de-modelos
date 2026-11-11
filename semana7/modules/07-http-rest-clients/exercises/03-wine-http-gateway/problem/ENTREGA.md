# Entrega assignment 7.2 - De gateway local a cliente HTTP

## Contrato

- URL: MODEL_API_URL + /v1/predictions
- Metodo: POST
- Cabecera: Accept: application/json
- Cuerpo: {"features": {...los 11 campos...}}
- Respuesta valida: 200 con {"prediction": {...}, "request_id": "..."}
- 422: los datos no cumplen el contrato de entrada
- 503: el modelo de la API no esta disponible

## Que he cambiado

Solo he tocado dos ficheros del starter:

1. src/model_ui/http_gateway.py. He completado predict, _read_object y _request_id.
2. app.py. En build_gateway, si hay MODEL_API_URL se crea HttpInferenceGateway. Si no hay, sigue como en S6 con DemoGateway o el bundle.

No he cambiado controller.py, presentation.py, session.py ni telemetry.py. La UI, el retry, el clear y la telemetria son los de S6. main ya leia MODEL_API_URL y el gateway se crea una vez con st.cache_resource.

## Traduccion de errores

- 422 -> InputContractError
- 503 -> ArtifactUnavailableError
- otro status que no sea 2xx -> BackendInferenceError
- timeout -> InferenceTimeoutError
- error de conexion -> ArtifactUnavailableError
- otro error de requests -> BackendInferenceError
- JSON roto, que no es un objeto o prediction que no cumple PredictionPayload -> BackendInferenceError

Los mensajes son fijos, asi que no se muestra el cuerpo de la API, ni trazas, ni las features. El controlador de S6 ya sabe convertir estos errores en un mensaje para el usuario.

## Comprobaciones

Desde la raiz del starter:

```
uv run python -m pytest -q
..................................                                       [100%]
34 passed in 0.92s
```

```
uv run ruff check src tests app.py
All checks passed!

uv run ruff format --check src tests app.py
17 files already formatted
```

Nota: con uv run pytest -q me sale ModuleNotFoundError: No module named 'app', porque pytest no mete la carpeta del starter en el path. Con python -m pytest si la mete y pasan todos.

## Recorrido con la API

Terminal 1, en la raiz del modulo:

```
uv run python examples/wine-quality-api/server.py
```

Terminal 2, en el starter:

```
MODEL_API_URL=http://127.0.0.1:8000 uv run streamlit run app.py
```

Exito: con los valores por defecto la app muestra "Requiere revision" e "Inferencia completada", con model_version wine-quality-demo-v1.

Fallo: arranco la API con --mode unavailable y la app muestra "Modelo no disponible", "Comprueba el bundle configurado o avisa al responsable tecnico", el Request ID y el boton Reintentar. La telemetria cuenta un error artifact_unavailable. No aparece ninguna traza ni las features.

Tambien probe el gateway directamente contra la API:

```
http://127.0.0.1:8000 OK quality_band='needs_review' confidence=0.71 req_de9f8488bf41
alcohol="alto" -> InputContractError, request_id req_4b7fbc235bbc
API en modo unavailable -> ArtifactUnavailableError, request_id req_ef2e475e82c9
API apagada -> ArtifactUnavailableError, request_id None
```

Modo demo: sin MODEL_API_URL arranco con uv run streamlit run app.py y la app sigue funcionando con DemoGateway. Sale "Inferencia completada" con model_version demo-ui-v1.
