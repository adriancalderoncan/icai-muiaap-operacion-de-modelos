"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

from dataclasses import dataclass
from pathlib import Path

import joblib

from model_inference.preprocess import FEATURE_NAMES, WineFeatures

# ruta por defecto del modelo
DEFAULT_MODEL_PATH = Path("models/wine_quality_classifier.joblib")


@dataclass(frozen=True)
class LoadedWineModel:
    """Modelo ya cargado y comprobado, junto con su version."""

    estimator: object
    model_version: str


def load_wine_quality_model(model_path: Path) -> LoadedWineModel:
    """Carga el .joblib y comprueba que es compatible antes de usarlo."""

    # El fichero exista
    if not model_path.is_file():
        raise FileNotFoundError(f"No se encontró el modelo en {model_path}")

    artefacto = joblib.load(model_path)

    # Sea un diccionario
    if not isinstance(artefacto, dict):
        raise ValueError("El artefacto debe ser un diccionario.")

    # Que las features sean las mismas y en el mismo orden
    feature_names = tuple(artefacto.get("feature_names", []))
    if feature_names != FEATURE_NAMES:
        raise ValueError(
            "Los feature_names del artefacto no coinciden con FEATURE_NAMES."
        )

    # Que tenga version
    model_version = artefacto.get("model_version")
    if not isinstance(model_version, str) or model_version == "":
        raise ValueError("El artefacto no tiene un model_version valido.")

    # Que tenga un estimador con predict y predict_proba
    estimator = artefacto.get("estimator")
    if not hasattr(estimator, "predict") or not hasattr(estimator, "predict_proba"):
        raise ValueError("El artefacto no contiene un clasificador compatible.")

    return LoadedWineModel(estimator=estimator, model_version=model_version)


def infer_wine_quality(
    model: LoadedWineModel, features: WineFeatures
) -> tuple[str, float]:
    """Predice la categoria y la confianza de ua muestra."""

    # sklearn espera una lista de filas, aqui solo hay una
    X = [features.as_vector()]

    quality_band = model.estimator.predict(X)[0]
    probabilidades = model.estimator.predict_proba(X)[0]
    confidence = max(probabilidades)

    return str(quality_band), round(float(confidence), 3)
