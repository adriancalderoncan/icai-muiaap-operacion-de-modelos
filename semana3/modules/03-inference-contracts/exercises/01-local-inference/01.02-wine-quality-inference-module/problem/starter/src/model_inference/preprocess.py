"""TODO: transformación de una muestra validada en el vector del modelo."""

from dataclasses import dataclass

from model_inference.contracts import WineQualityRequest

# version del preprocesado, se devuelve con cada prediccion
PREPROCESSING_VERSION = "wine-red-features-v1"

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden aleatorio del CSV.


@dataclass(frozen=True)
class WineFeatures:
    """Las 11 features ya validadas."""

    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    ph: float
    sulphates: float
    alcohol: float

    def as_vector(self) -> list[float]:
        """Devuelve la lista de 11 numeros en el orden de FEATURE_NAMES."""
        vector = []
        for name in FEATURE_NAMES:
            vector.append(getattr(self, name))
        return vector


def preprocess_wine_request(request: WineQualityRequest) -> WineFeatures:
    """Pasa del request validado a las features del modelo."""
    datos = request.model_dump()
    return WineFeatures(**datos)
