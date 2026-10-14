# Starter — Módulo local de inferencia de vino

Este es el único proyecto de código que recibe el alumnado. Implementad los
`TODO` siguiendo el orden del `../readme.md` y haced pasar las pruebas sin mirar
la solución del profesorado.

El profesor colocará `wine_quality_classifier.joblib` dentro de `models/` antes
del taller. El modelo ya está entrenado: no hay que modificarlo ni reentrenarlo.

## Entrega — cómo ejecutarlo

Desde esta carpeta (starter/), con el modelo en models/wine_quality_classifier.joblib:

```bash
uv sync
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run python -m model_inference.predict_file \
  --input assets/inference_samples.csv \
  --output .tmp/wine_predictions.csv
```

Resultado: 11 tests en verde, Ruff sin errores y este CSV de salida:

```text
sample_id,quality_band,confidence,model_version,preprocessing_version
red-001,needs_review,0.767,wine-quality-rf-v1,wine-red-features-v1
red-002,needs_review,0.801,wine-quality-rf-v1,wine-red-features-v1
red-003,acceptable,0.581,wine-quality-rf-v1,wine-red-features-v1
red-004,needs_review,0.661,wine-quality-rf-v1,wine-red-features-v1
red-005,needs_review,0.466,wine-quality-rf-v1,wine-red-features-v1
```

Si una fila no cumple el contrato (columna extra, campo que falta o valor
fuera de rango), el comando muestra la fila, el sample_id y el campo que
falla, termina con código 2 y no crea el CSV de salida.

### Responsabilidades

Archivo y Qué hace 
**contracts.py**: Contrato de entrada (11 features, rangos, sin columnas extra) y de salida (categoría, confianza y versiones). 
**preprocess.py**: FEATURE_NAMES, versión del preprocesado y paso del request validado al vector ordenado. 
**inference.py**: Carga el .joblib, comprueba que es compatible y predice categoría y confianza. 
**predict_file.py  El comando: lee el CSV, llama a los otros tres y escribe la salida solo si todo es válido. 

### Los tests como relas de la API local

Test y Regla 
**test_preprocess_preserves_feature_order**: El vector sale en el orden de FEATURE_NAMES. 
**writes_predictions_for_kaggle_rows**: Una fila válida da una predicción con categoría, confianza y las dos versiones. 
**writes_all_requested_rows**: Hay una fila de salida por cada fila de entrada, en el mismo orden y con las 5 columnas. 
**rejects_an_unknown_csv_column**: Una columna que no está en el contrato se rechaza. 
**rejects_a_missing_required_field**: Si falta una feature se rechaza. 
**rejects_an_out_of_range_field**: Un valor fuera de rango (por ejemplo ph=99) se rechaza. 
**leaves_no_output_when_a_later_row_is_invalid**: Si una fila posterior falla, no queda CSV de salida y el error dice qué sample_id es. 
**rejects_an_invalid_prediction_category**: Si el modelo devuelve una categoría que no existe, se rechaza (se valida también la salida). 
**rejects_an_incomplete_model_artifact**: Un artefacto sin estimador se rechaza antes de predecir. 
**rejects_an_empty_sample_id>**; Cada fila necesita un sample_id no vacío. 
**rejects_an_incompatible_model_artifact**: Si los feature_names del modelo están en otro orden, se rechaza. 

En todos los casos de error el comando termina con código 2 y no crea el CSV.

### Dos decisiones de diseño

1. **Comprobar el artefacto antes de usarlo.** El .joblib guarda los
   feature_names con los que se entrenó. Al cargarlo comparo ese orden con
   FEATURE_NAMES y compruebo que tiene predict y predict_proba. 
2. **Todo o nada al escribir.** Primero valido y predgo todas las filas en
   memoria y solo al final, si no hay errores, escribo el CSV. 
