"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import joblib
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import (
    FEATURE_NAMES,
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1)

    @field_validator("schema_version")
    @classmethod
    def check_schema_version(cls, value: str) -> str:
        if value != ARTIFACT_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version incompatible: se esperaba {ARTIFACT_SCHEMA_VERSION}"
            )
        return value

    @field_validator("preprocessing_version")
    @classmethod
    def check_preprocessing_version(cls, value: str) -> str:
        if value != PREPROCESSING_VERSION:
            raise ValueError(
                f"preprocessing_version incompatible: se esperaba "
                f"{PREPROCESSING_VERSION}"
            )
        return value

    @field_validator("feature_names")
    @classmethod
    def check_feature_names(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != FEATURE_NAMES:
            raise ValueError("feature_names no coincde con el orden de la semana 3")
        return value

    @field_validator("output_labels")
    @classmethod
    def check_output_labels(
        cls, value: tuple[QualityBand, ...]
    ) -> tuple[QualityBand, ...]:
        if value != OUTPUT_LABELS:
            raise ValueError(f"output_labels debe ser {list(OUTPUT_LABELS)}")
        return value


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def check_estimator(estimator: object, estimator_type: str) -> None:
    """Comprueba la interfaz y la clase del estimador."""

    for method in ("predict", "predict_proba"):
        if not callable(getattr(estimator, method, None)):
            raise ValueError(f"El estimador no tiene el método {method}")
    if type(estimator).__name__ != estimator_type:
        raise ValueError(
            f"El estimador es {type(estimator).__name__} pero el manifiesto "
            f"dice {estimator_type}"
        )


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """TODO: devuelve un manifiesto compatible con el contrato."""

    check_estimator(estimator, type(estimator).__name__)
    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""

    if manifest is None:
        raise ValueError("Hace falta un manifiesto para guardar el bundle")
    check_estimator(estimator, manifest.estimator_type)

    bundle_path.mkdir(parents=True, exist_ok=True)
    (bundle_path / MANIFEST_FILENAME).write_text(
        manifest.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    joblib.dump(estimator, bundle_path / MODEL_FILENAME)
    return manifest


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """TODO: valida el manifiesto antes de cargar el estimador."""

    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"No existe {manifest_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"No existe {model_path}")

    try:
        manifest = ArtifactManifest.model_validate_json(
            manifest_path.read_text(encoding="utf-8")
        )
    except ValidationError as error:
        raise ValueError(f"manifest.json no es valido:\n{error}") from error

    estimator = joblib.load(model_path)
    check_estimator(estimator, manifest.estimator_type)
    return LoadedModelBundle(estimator=estimator, manifest=manifest)


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    features = preprocess_wine_request(request).as_vector()
    label = str(bundle.estimator.predict([features])[0])
    probabilities = bundle.estimator.predict_proba([features])[0]

    if label not in bundle.manifest.output_labels:
        raise ValueError(
            f"El modelo ha devuelto la etiqueta {label}, que no esta en output_labels"
        )

    try:
        return WineQualityPrediction(
            quality_band=label,
            confidence=float(max(probabilities)),
            model_version=bundle.manifest.model_version,
            preprocessing_version=bundle.manifest.preprocessing_version,
        )
    except ValidationError as error:
        raise ValueError(
            f"El modelo ha devuelto una salida no valida:\n{error}"
        ) from error
