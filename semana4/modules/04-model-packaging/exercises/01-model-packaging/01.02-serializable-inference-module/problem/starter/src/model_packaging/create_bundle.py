"""Crea el bundle a partir del payload joblib de la semana 3."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    create_manifest,
    save_model_bundle,
)
from model_packaging.preprocess import FEATURE_NAMES


def create_bundle(legacy_path: Path, bundle_path: Path) -> None:
    """Convierte el payload legado en manifest.json y model.joblib."""

    payload = joblib.load(legacy_path)
    if tuple(payload["feature_names"]) != FEATURE_NAMES:
        raise ValueError("feature_names del payload no coincide con la semana 3")

    estimator = payload["estimator"]
    manifest = create_manifest(estimator, payload["model_version"])
    save_model_bundle(bundle_path, estimator, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    arguments = parser.parse_args()
    create_bundle(arguments.legacy, arguments.bundle)
    print(f"Bundle creado en {arguments.bundle}")


if __name__ == "__main__":
    main()
