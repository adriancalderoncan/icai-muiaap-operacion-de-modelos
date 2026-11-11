# Entrega assignment 7.1 - De curl a un cliente Python

## Cliente

He completado starter/client.py sin tocar la API de bombas. La funcion hace esto:

1. Manda un POST a /v1/predictions con json=payload, la cabecera Accept: application/json y un timeout.
2. Llama a raise_for_status para que un 422 no se tome como una prediccion buena.
3. Si hay HTTPError lanza PredictionClientError con el status. Si hay Timeout o ConnectionError lanza PredictionClientError con un mensaje distinto para cada uno.
4. Lee la respuesta con .json() y si no es un diccionario lanza error.

## Tests

```
uv run python -m unittest discover -s exercises/02-api-client-lab/problem/starter -p "test_*.py" -v
```

```
test_converts_connection_error ... ok
test_converts_http_error_and_preserves_status ... ok
test_converts_timeout ... ok
test_rejects_success_json_that_is_not_an_object ... ok
test_sends_json_accept_and_timeout ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK
```

## Evidencia HTTP

GET /health

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
X-Request-Id: req_322559b63247

{"status": "ok", "service": "pump-maintenance-prediction", "model_status": "ready", "model_version": "pump-risk-1.0.0", "request_id": "req_322559b63247"}
```

POST /v1/predictions con prediction-valid.json

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
X-Request-Id: req_d05073cca71e

{"machine_id": "pump-017", "prediction": {"label": "maintenance_required", "risk_score": 0.85}, "model_version": "pump-risk-1.0.0", "request_id": "req_d05073cca71e"}
```

POST /v1/predictions con prediction-invalid.json

```
HTTP/1.1 422 Unprocessable Content
Content-Type: application/json; charset=utf-8
X-Request-Id: req_27cdcd55e27e

{"error": {"code": "validation_error", "message": "JSON is valid but violates the input contract", "fields": [{"field": "measurements.vibration_mm_s", "message": "must be a number"}]}, "request_id": "req_27cdcd55e27e"}
```

Resumen:

- health: 200, request_id req_322559b63247
- POST valido: 200, request_id req_d05073cca71e. maintenance_required es el resultado del modelo, no un error.
- POST invalido: 422, request_id req_27cdcd55e27e, campo rechazado measurements.vibration_mm_s

Es 422 y no 400 porque el JSON se puede leer bien, el problema es que vibration_mm_s no es un numero y eso incumple el contrato. Un 400 seria si el JSON estuviera roto.

## Decision

No se reintenta un POST ciegamente porque POST no es idempotente: si la primera peticion llego al servidor y solo se perdio la respuesta, al repetirla se crearia otra prediccion. Ademas si el error es un 422 reintentar no sirve, va a fallar igual.
