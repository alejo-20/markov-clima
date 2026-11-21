# Design

## Context

El repositorio parte vacío, por lo que no hay restricciones de código heredado. La entrada del modelo es una matriz 4x4 de transición entre Soleado, Nublado, Lluvioso y Tormenta; todas sus entradas son estrictamente positivas, lo que garantiza una cadena regular y una distribución estacionaria única. Los artefactos de esta especificación se escriben antes de cualquier código de aplicación.

## Goals / Non-Goals

**Goals:**

- Mantener la lógica matemática independiente de FastAPI para poder probarla de forma aislada.
- Calcular distribuciones a 1, 3, 5 y 10 pasos y la evolución completa de 0 a 10 pasos.
- Validar todas las entradas con mensajes comprensibles en español.
- Ofrecer una UI sin build que funcione servida por el propio FastAPI.

**Non-Goals:**

- Ajustar el modelo con datos observados.
- Persistir configuraciones entre recargas del navegador.
- Soportar más de un modelo de Markov distinto del discreto de tiempo discreto.

## Decisions

### Arquitectura

Tres capas con una sola dirección de dependencia: `app/markov.py` (funciones puras sobre NumPy) ← `app/main.py` (API, modelos Pydantic y archivos estáticos) ← `app/static/` (HTML/CSS/JS que consume la API). El frontend no calcula la cadena: envía el estado o vector inicial, los pasos y, opcionalmente, una matriz editada.

### Modelo matemático

Si π_0 es un vector fila de distribución inicial y P la matriz de transición, entonces π_n = π_0 · P^n. Para un estado inicial i, π_0 = e_i (vector unitario). P^0 es la identidad. La distribución estacionaria π satisface π·P = π y ∑π = 1; se obtiene elevando P a un n grande (por ejemplo 1000), normalizando el resultado y verificando que ‖π·P − π‖∞ sea menor que la tolerancia.

### Validación y tolerancias

La matriz debe ser cuadrada, tener al menos 3 filas, todos los valores en [0, 1] y cada fila debe sumar 1 con tolerancia absoluta 1e-9. Los estados deben ser únicos y no vacíos. Los pasos deben ser enteros no negativos. El vector inicial debe tener la longitud de la matriz, ser no negativo y sumar 1 con la misma tolerancia.

### Decisiones técnicas

- NumPy para potenciación y álgebra lineal; `np.linalg.matrix_power` para P^n.
- FastAPI + Pydantic para el contrato JSON y la documentación automática.
- Errores de dominio como `ValueError` en el motor; la API los transforma en respuestas 422 con un `detail` explícito.
- Chart.js por CDN para barras agrupadas y líneas; la tabla numérica siempre se renderiza aunque falle el CDN.
- La matriz por defecto vive en el backend; la UI permite enviar una matriz alternativa sin mutar el estado global del servidor.

### Manejo de errores

- Datos mal formados o reglas de negocio violadas → HTTP 422 con mensaje que nombra el campo o la fila problemática.
- Errores inesperados → HTTP 500 con mensaje genérico, sin exponer trazas al cliente.
- En la UI, cualquier respuesta no exitosa o error de red se muestra en un bloque de mensajes y no sobrescribe resultados anteriores.

## Risks / Trade-offs

- Comparaciones en coma flotante: se mitiga con la tolerancia 1e-9 documentada.
- Chart.js depende de CDN: se mitigar mostrando la tabla de valores y un mensaje si la librería no carga.
- Elevación a potencias muy grandes: se acota el número de pasos admitidos por la API para evitar costos innecesarios.
