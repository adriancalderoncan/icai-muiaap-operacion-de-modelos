# wine-quality

Proyecto `uv` con el entrenamiento del caso Wine de la semana 1. Parte de los
tres archivos de `semana2/starter` y los organiza como un paquete de Python
con sus datos, sus tests y un entorno bloqueado con `uv.lock`.

El modelo es un `ExtraTreesClassifier` que predice la calidad del vino
(clases 3 a 8) a partir de 11 variables físico-químicas. Se evalúa con F1
macro sobre un 15 % de validación y usa `random_state=42` para que el
resultado se repita.

## Requisitos

- [uv](https://docs.astral.sh/uv/)
- Git
- Una terminal Bash

## Estructura

```text
semana2/wine-quality-project/
├── pyproject.toml              # dependencias del proyecto
├── uv.lock                     # versiones exactas
├── data/raw/WineQT.csv         # dataset original (1143 filas)
├── src/wine_quality/train.py   # carga de datos, entrenamiento y métrica
└── tests/test_train.py         # test del entrenamiento
```

De dónde sale cada archivo:

| Starter | Destino |
| --- | --- |
| `semana2/starter/WineQT.csv` | `data/raw/WineQT.csv` |
| `semana2/starter/train.py` | `src/wine_quality/train.py` |
| `semana2/starter/test_train.py` | `tests/test_train.py` |

## Instalación

Desde la raíz del fork:

```bash
cd semana2/wine-quality-project
uv sync --locked
```

`--locked` instala exactamente las versiones de `uv.lock` y falla si el lock
no coincide con `pyproject.toml`, así no se resuelven versiones nuevas.
pandas y scikit-learn son dependencias normales y Pytest y Ruff son
dependencias de desarrollo.

## Ejecución

```bash
uv run --frozen python -m wine_quality.train
```

Salida esperada:

```text
Filas: 1143
Variables: 11
Clases: 6
F1 macro: 0.3402
```

## Comprobaciones

```bash
uv run --frozen pytest
uv run --frozen ruff check .
```

El test comprueba la forma del dataset, las clases, que la columna `Id` no se
usa como variable y que dos entrenamientos seguidos dan la misma métrica.
Ruff no debe mostrar errores.
