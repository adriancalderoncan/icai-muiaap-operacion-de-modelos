# Entrega practica 6.2

## Que se mantiene de S5 y que se añade

Se mantiene igual el formulario (FEATURE_FIELDS y collect_values), build_gateway y el gateway del bundle de S4.

Lo nuevo:
- session.py: guarda last_state, telemetry y last_values. Limpiar vuelve a idle pero no borra la telemetria.
- policies.py: confianza low si es menor de 0.60, medium hasta 0.85 y high desde 0.85. Latencia lenta si pasa de 300 ms.
- presentation.py: prepara lo que se muestra del resultado y convierte los errores en mensajes con recuperacion y request_id.
- controller.py: pasa por loading, mide la latencia y acaba en success o error. Apunta en la telemetria solo datos agregados.
- app.py: cachea el gateway con st.cache_resource y dibuja los estados. Tambien vaciamos el hueco de carga porque si no el resultado salia dos veces.

## Tests

```
uv run pytest -q
8 passed
```

ruff check y ruff format --check sin errores.

## Pruebas en la app

- Inicio: sale el mensaje de completar el formulario y la telemetria a 0.
- Loading: con el bundle real dura muy poco y no da tiempo a verlo. Lo comprueba test_controller.py.
- Exito: con los valores por defecto sale Requiere revision, confianza 77% y latencia 39 ms.
- Confianza baja: con Alcohol 12.5 sale confianza 59% y el aviso de que no es una garantia.
- Rerun: pulsando R el resultado sigue ahi.
- Trazabilidad: en el expander salen las dos versiones y el request_id.
- Limpiar: vuelve a idle y la telemetria sigue con 1 peticion.
- Bundle ausente: con una ruta que no existe sale "Modelo no disponible", que hacer y el request_id. No sale traceback ni la ruta.
- Reintentar: sale otro request_id y la telemetria cuenta 2 errores.

El error de contrato y la respuesta lenta no se pueden provocar desde el formulario, asi que los probamos con el controlador:

```
DemoGateway(confidence=0.51, delay_seconds=0.4)
success low above_target 400

muestra con un campo de mas
error invalid_input
```

La telemetria de abajo es de esta prueba.

## Cache

Cacheamos el gateway porque cargar el bundle cuesta y es el mismo para todos. No guarda nada de ninguna peticion, eso va en st.session_state.

## Telemetria

```
TelemetrySnapshot(requests_total=2, requests_success=1, requests_error=1, errors_by_code={'invalid_input': 1}, latency_mean_ms=200.075, latency_p95_ms=400.138, model_versions=('demo-ui-v1',), preprocessing_versions=('wine-red-features-v1',))
```

Solo hay contadores, errores, latencias y versiones. No aparecen las features.

## Para S7

- El controller no usa Streamlit, asi que se puede cambiar el gateway por uno HTTP.
- Se mantienen los estados, los mensajes de error, las politicas y la telemetria.
