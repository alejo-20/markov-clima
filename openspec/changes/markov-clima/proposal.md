# Proposal

## Why

Predecir el clima diario en Bogotá a partir de una cadena de Markov discreta requiere calcular distribuciones a varios horizontes temporales; hacerlo a mano es repetitivo y propenso a errores. Además, el proyecto necesita evidenciar un flujo de desarrollo dirigido por especificaciones (SDD) en el que el comportamiento acordado preceda a cualquier código de la aplicación.

## What Changes

- Se define un motor matemático puro que valida la matriz de transición y calcula potencias, distribuciones en n pasos y la distribución estacionaria.
- Se expone una API REST con FastAPI para consultar el modelo y obtener predicciones a 1, 3, 5 y 10 pasos.
- Se crea una interfaz web en español que permite elegir el estado inicial, editar la matriz, calcular, visualizar gráficas y consultar valores numéricos.
- Se incorporan pruebas automatizadas trazables a cada requisito y documentación del proceso SDD/OpenSpec.

## Scope

- Modelo con cuatro estados: Soleado, Nublado, Lluvioso y Tormenta, con la matriz de transición proporcionada.
- Validación de matriz cuadrada, valores en [0, 1], filas que suman 1 con tolerancia 1e-9 y mínimo tres estados.
- Cálculo de π_n = π_0 · P^n desde un estado inicial o desde un vector inicial, para los pasos 1, 3, 5 y 10 y para la evolución 0..10.
- Cálculo de la distribución estacionaria como referencia.
- API con errores 422 descriptivos y UI responsive servida por FastAPI sin proceso de build.

## Out of Scope

- Datos climáticos reales, series históricas o entrenamiento/estimación de la matriz.
- Modelos ocultos de Markov, cadenas continuas o pronósticos geográficos.
- Persistencia en base de datos, autenticación, usuarios o despliegue en producción.
- Dependencias de frontend que requieran compilación (bundlers, frameworks JavaScript).

## Capabilities

### New Capabilities

- `markov-engine`: validación del modelo y cálculos de potencias, distribuciones en n pasos y distribución estacionaria.
- `api`: endpoints REST para consultar el modelo y pedir predicciones, con errores de validación claros.
- `web-ui`: interfaz en español para configurar el modelo, visualizar resultados y mostrar errores.

### Modified Capabilities

_Ninguna._

## Impact

Se añaden `app/markov.py`, `app/main.py`, `app/static/`, `tests/`, `requirements.txt`, `README.md` y el directorio `openspec/` con el ciclo de vida del change. Las dependencias son Python 3.11+, FastAPI, NumPy, Uvicorn, pytest, httpx y pytest-cov; Chart.js se carga por CDN.
