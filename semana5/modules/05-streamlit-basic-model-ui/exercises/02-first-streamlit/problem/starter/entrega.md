# Entrega practica 5.2

## Bundle

Usamos el bundle de nuestra practica de S4 (manifest.json y model.joblib).

El cargador espera que model.joblib tenga un diccionario con la clave estimator y el nuestro guardaba el modelo directamente, asi que guardamos el mismo modelo de esa forma en la carpeta wine_quality_bundle_s5.

Para arrancar desde la carpeta del starter:

```
uv sync
$env:MODEL_UI_BUNDLE = 'C:\ruta\al\repo\semana4\modules\04-model-packaging\exercises\01-model-packaging\01.02-serializable-inference-module\problem\starter\models\wine_quality_bundle_s5'
uv run --with 'streamlit>=1.40,<2.0' streamlit run app.py
```

## Tests

```
uv run python -m pytest -q
27 passed
```

ruff check y ruff format --check sin errores.

## QA manual

1. Arranque con bundle: salen los 11 campos y no se hace ninguna inferencia.
2. Edicion sin envio: cambiamos Alcohol a 12.5 y no sale ninguna prediccion.
3. Submit valido: sale quality_band acceptable, confidence 0.59, model_version wine-quality-rf-v1 y preprocessing_version wine-red-features-v1.
4. Bundle ausente: sin MODEL_UI_BUNDLE sale "No se pudo cargar el bundle de S4" y que configuremos MODEL_UI_BUNDLE. No sale ninguna ruta ni traceback.

## Limites para S6

- El resultado se pierde en el siguiente rerun.
- El bundle se carga otra vez en cada rerun.
- No hay estado de carga, ni reintentar, ni limpiar.
- No se mide la latencia ni hay telemetria.
