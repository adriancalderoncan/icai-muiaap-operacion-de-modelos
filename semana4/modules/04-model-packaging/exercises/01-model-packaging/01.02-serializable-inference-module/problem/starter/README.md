# Starter — Bundle serializado de calidad de vino

Este es el único proyecto de código que recibe el alumnado. Los contratos de
entrada y el orden de las características ya vienen resueltos para que el
taller se concentre en serialización, carga y validación.

Implementad los TODO de src/model_packaging/artifact.py y
src/model_packaging/predict_file.py en el orden indicado por ../readme.md. Las
pruebas de tests/ son la especificación ejecutable.

El artefacto real del profesor, si se usa, debe vivir en
models/wine_quality_bundle/; esa carpeta se ignora y no se entrega dentro del
repositorio del alumnado.

## Nota de compatibilidad

1. **Cambiar el orden de feature_names.** Si en el manifiesto se intercambian density y alcohol, el modelo seguiría recibiendo once números y predeciría sin dar error, pero con las medidas en otra posición. Por eso la carga compara feature_names con FEATURE_NAMES antes de hacer joblib.load y se para.
2. **Cambiar preprocessing_version.** Si el modelo se entrenó con otro preprocesado, el vector que construye preprocess.py no es el que espera el
modelo, aunque model_version sea el mismo. La carga solo acepta wine-red-features-v1 y rechaza cualquier otra versión antes de inferir.
