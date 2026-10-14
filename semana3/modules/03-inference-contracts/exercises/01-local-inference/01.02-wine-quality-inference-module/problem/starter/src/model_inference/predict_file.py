"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.
import argparse
import csv
import os
import sys
from pathlib import Path

from pydantic import ValidationError

from model_inference.contracts import WineQualityPrediction, WineQualityRequest
from model_inference.inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from model_inference.preprocess import PREPROCESSING_VERSION, preprocess_wine_request

# columnas del csv de salida, en este orden
OUTPUT_FIELDS = [
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
]


def predict_file(input_path: Path, output_path: Path, model_path: Path) -> int:
    """Lee el csv, predice cada fila y escribe el csv de salida."""

    # primero cargo el modelo, si esta mal no merece la pena leer nada
    model = load_wine_quality_model(model_path)

    predicciones = []

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames or "sample_id" not in reader.fieldnames:
            raise ValueError("El CSV de entrada tiene que tener la columna sample_id.")

        # empiezo en 2 porque la fila 1 es la cabecera
        for numero_fila, row in enumerate(reader, start=2):
            # Perimero separo el sample_id, no entra al modelo
            sample_id = row.pop("sample_id")
            if not sample_id or not sample_id.strip():
                raise ValueError(f"Fila {numero_fila}: el sample_id esta vacio.")

            # Segundo, contrato de entrada
            try:
                request = WineQualityRequest.model_validate(row)
            except ValidationError as error:
                raise ValueError(
                    f"Fila {numero_fila} (sample_id={sample_id}) no es valida:\n{error}"
                ) from error

            #  Tercero, preprocesado e inferencia
            features = preprocess_wine_request(request)
            quality_band, confidence = infer_wine_quality(model, features)

            # Quinto, contrato de salida
            try:
                prediccion = WineQualityPrediction(
                    quality_band=quality_band,
                    confidence=confidence,
                    model_version=model.model_version,
                    preprocessing_version=PREPROCESSING_VERSION,
                )
            except ValidationError as error:
                raise ValueError(
                    f"Fila {numero_fila} (sample_id={sample_id}): "
                    f"el modelo ha devuelto una salida no valida:\n{error}"
                ) from error

            # guardo en memoria, todavia no escribo nada
            predicciones.append({"sample_id": sample_id, **prediccion.model_dump()})

    # solo llego aqui si todas las filas son validas, entonces ahora si escribo
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # escribo primero en un fichero temporal y al final lo renombro.
    # os.replace es atomico: el csv final o no existe o esta completo,
    # aunque falle algo a mitad de escribir
    tmp_path = output_path.with_name(output_path.name + ".tmp")
    try:
        with tmp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(predicciones)
        os.replace(tmp_path, output_path)
    finally:
        # si algo ha fallado borro el temporal para no dejar nada erroneo
        tmp_path.unlink(missing_ok=True)

    return len(predicciones)


def main() -> int:
    """Lee los argumentos, ejecuta la prediccion y gestiona los errores."""

    parser = argparse.ArgumentParser(description="Inferencia de calidad de vino")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path)
    args = parser.parse_args()

    try:
        n = predict_file(args.input, args.output, args.model)
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Predicciones escritas: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
