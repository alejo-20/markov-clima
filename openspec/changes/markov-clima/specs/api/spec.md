# Spec Delta

## Purpose

Esta capacidad define el contrato HTTP mediante el cual los clientes consultan el modelo y solicitan predicciones, incluyendo respuestas de error interpretables.

## ADDED Requirements

### Requirement: API-01 Consulta del modelo

El sistema MUST exponer GET /api/model con los estados y la matriz de transición vigente.

#### Scenario: API-01-S1 modelo por defecto

- **WHEN** se llama a GET /api/model sin parámetros
- **THEN** se responde 200 con la lista de cuatro estados y la matriz 4x4 de Bogotá

### Requirement: API-02 Predicción de distribuciones

El sistema MUST exponer POST /api/predict que acepte un estado inicial o un vector inicial, una lista de pasos y una matriz opcional, y devuelva las distribuciones solicitadas.

#### Scenario: API-02-S1 predicción desde estado inicial

- **WHEN** se envía {"initial_state": "Lluvioso", "steps": [1, 3, 5, 10]}
- **THEN** se responde 200 con una distribución por paso, cada una de 4 valores que suman 1

#### Scenario: API-02-S2 predicción desde vector inicial

- **WHEN** se envía un vector inicial válido en lugar de un estado
- **THEN** se responde 200 con las distribuciones calculadas como π_0 · P^n

#### Scenario: API-02-S3 matriz personalizada

- **WHEN** se envía una matriz válida distinta de la predeterminada junto con los estados correspondientes
- **THEN** la predicción se calcula con esa matriz y la respuesta incluye la matriz y los estados usados

#### Scenario: API-02-S4 evolución completa y estacionaria

- **WHEN** se solicitan los pasos 1, 3, 5 y 10 junto con la opción de evolución y distribución estacionaria
- **THEN** la respuesta incluye la evolución de 0 a 10 pasos por estado y la distribución estacionaria de referencia

### Requirement: API-03 Errores de validación claros

El sistema MUST responder con HTTP 422 y un mensaje descriptivo cuando la petición viole una regla del modelo.

#### Scenario: API-03-S1 estado desconocido

- **WHEN** se envía un initial_state que no existe en el modelo
- **THEN** se responde 422 con un detail que menciona los estados válidos

#### Scenario: API-03-S2 pasos inválidos

- **WHEN** se envían pasos negativos, vacíos o no enteros
- **THEN** se responde 422 con un detail que explica que los pasos deben ser enteros no negativos

#### Scenario: API-03-S3 matriz inválida

- **WHEN** se envía una matriz con una fila que no suma 1 o con valores fuera de [0, 1]
- **THEN** se responde 422 con un detail que identifica el problema y no se calcula ninguna predicción

#### Scenario: API-03-S4 entrada mutuamente excluyente

- **WHEN** se envían simultáneamente initial_state y un vector inicial
- **THEN** se responde 422 con un detail que indica que debe elegirse solo una opción

#### Scenario: API-03-S5 ninguna entrada inicial

- **WHEN** no se envía ni estado ni vector inicial
- **THEN** se responde 422 con un detail que exige una de las dos opciones
