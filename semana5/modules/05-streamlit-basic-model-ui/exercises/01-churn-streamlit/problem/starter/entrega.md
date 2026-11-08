# Entrega practica 5.1

Antes de ejecutar pensamos que el perfil 2, 95, 4, False daria Baja probable (0.95) y el 36, 35, 0, True Permanencia probable (0.05). Al probarlo salio eso.

## Tests

```
uv run python -m pytest -q
13 passed
```

ruff check y ruff format --check sin errores.

## QA manual

1. Arranque: sale el titulo y el formulario con los 4 campos. No hay prediccion.
2. Edicion sin envio: cambiamos el gasto a 95 y no pasa nada hasta pulsar el boton.
3. Submit valido: con 12, 95, 1, False sale Baja probable, score 0.65 y la explicacion.
4. Resultado actualizado: marcamos contrato anual, volvemos a enviar y sale Permanencia probable con 0.3. El resultado anterior ya no aparece.

Para Wine se mantiene lo mismo: formulrio, boton y una sola llamada al modelo al enviar. Cambian los campos y en vez de predict() se usa el gateway del bundle.
