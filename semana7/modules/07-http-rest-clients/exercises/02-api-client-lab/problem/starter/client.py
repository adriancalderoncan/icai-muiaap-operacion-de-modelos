"""Starter del cliente HTTP. Completa los TODO sin modificar la API."""

from __future__ import annotations

from typing import Any

# El TODO de la práctica usará este cliente para realizar la petición HTTP.
import requests


class PredictionClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def request_prediction(
    payload: dict[str, Any],
    *,
    base_url: str = "http://127.0.0.1:8000",
    timeout: float = 5.0,
    session: Any | None = None,
) -> dict[str, Any]:
    """Envía una predicción y devuelve un objeto JSON de respuesta."""
    # TODO 3: selecciona `session` o `requests` y envía POST con `json=`,
    # `Accept` y `timeout`. Comprueba los argumentos con test_client.py.
    # TODO 4: llama a `raise_for_status()` y conserva el status de HTTPError.
    # TODO 5: traduce Timeout y ConnectionError a PredictionClientError.
    # TODO 6: convierte la respuesta con `.json()` y exige un diccionario.
    if session is None:
        session = requests
    url = base_url.rstrip("/") + "/v1/predictions"
    try:
        response = session.post(
            url,
            json=payload,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        status = error.response.status_code
        raise PredictionClientError(
            f"La API respondio con error HTTP {status}", status_code=status
        ) from error
    except requests.Timeout as error:
        raise PredictionClientError(
            "La API ha tardado demasiado en responder"
        ) from error
    except requests.ConnectionError as error:
        raise PredictionClientError(
            "No se ha podido conectar con la API, revisa la URL"
        ) from error

    body = response.json()
    if not isinstance(body, dict):
        raise PredictionClientError("La respuesta no es un objeto JSON")
    return body
