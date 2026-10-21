"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

from pydantic import ValidationError

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest

OUTPUT_FIELDS = [
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
]


def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """TODO: valida todas las filas y escribe el CSV solo al final."""

    bundle = load_model_bundle(bundle_path)
    predictions = []

    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "sample_id" not in reader.fieldnames:
            raise ValueError("El CSV de entrada tiene que teer la columna sample_id")

        for row_number, row in enumerate(reader, start=2):
            sample_id = row.pop("sample_id")
            if not sample_id or not sample_id.strip():
                raise ValueError(f"Fila {row_number}: el sample_id esta vacio")

            try:
                request = WineQualityRequest.model_validate(row)
            except ValidationError as error:
                raise ValueError(
                    f"Fila {row_number} (sample_id={sample_id}) no es valida:\n{error}"
                ) from error

            try:
                prediction = infer_wine_quality(bundle, request)
            except ValueError as error:
                raise ValueError(
                    f"Fila {row_number} (sample_id={sample_id}): {error}"
                ) from error

            predictions.append({"sample_id": sample_id, **prediction.model_dump()})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_name(output_path.name + ".tmp")
    try:
        with tmp_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(predictions)
        os.replace(tmp_path, output_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return len(predictions)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


def main() -> int:
    """Ejecuta el comando y muestra los errores sin traceback."""

    arguments = parse_args()
    try:
        count = predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Predicciones escritas: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
