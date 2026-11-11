import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)


def definir_tool():
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": "Calcula la probabilidad de impago de una solicitud de prestamo",
            "parameters": PrestamoEntrada.model_json_schema(),
        },
    }


def ejecutar_tool(nombre, argumentos_json):
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": "La tool " + str(nombre) + " no existe"}
    argumentos = leer_argumentos(argumentos_json)
    try:
        entrada = PrestamoEntrada(**argumentos)
    except ValidationError as error:
        return {"ok": False, "error": str(error)}
    salida = predecir(entrada)
    return {
        "ok": True,
        "probabilidad_impago": salida.probabilidad_impago,
        "decision": salida.decision,
    }


def responder(mensajes, llm):
    historial = [{"role": "system", "content": SISTEMA}]
    for mensaje in mensajes:
        historial.append(mensaje.model_dump())
    herramientas = [definir_tool()]
    herramienta = None

    for vuelta in range(MAX_VUELTAS):
        respuesta = llm.completar(historial, herramientas)
        if not respuesta.get("tool_calls"):
            return ChatSalida(respuesta=respuesta["content"], herramienta=herramienta)

        historial.append(respuesta)
        for llamada in respuesta["tool_calls"]:
            nombre = llamada["function"]["name"]
            argumentos = llamada["function"]["arguments"]
            resultado = ejecutar_tool(nombre, argumentos)
            herramienta = HerramientaUsada(
                nombre=nombre, argumentos=leer_argumentos(argumentos), resultado=resultado
            )
            historial.append(
                {"role": "tool", "tool_call_id": llamada["id"], "content": json.dumps(resultado)}
            )

    return ChatSalida(
        respuesta="No he podido calcular el riesgo. Revisa los datos e intentalo otra vez.",
        herramienta=herramienta,
    )
