# markov-engine Specification

## Purpose

Esta capacidad define el motor matemático aislado que valida el modelo y produce todas las distribuciones necesarias para simular la cadena de Markov del clima en Bogotá.

## Requirements

### Requirement: ME-01 Validación de matriz de transición

El motor MUST aceptar únicamente matrices cuadradas de al menos 3 estados, con valores en [0, 1] y filas que sumen 1 con tolerancia 1e-9, y MUST rechazar cualquier otra entrada con un error descriptivo.

#### Scenario: ME-01-S1 matriz válida aceptada

- **WHEN** se valida la matriz 4x4 de Bogotá junto con sus cuatro estados únicos
- **THEN** la validación termina sin errores y devuelve la matriz como arreglo NumPy de coma flotante

#### Scenario: ME-01-S2 matriz no cuadrada rechazada

- **WHEN** se intenta validar una matriz cuyo número de filas difiere del número de columnas
- **THEN** se lanza un ValueError que indica que la matriz debe ser cuadrada

#### Scenario: ME-01-S3 fila que no suma 1 rechazada

- **WHEN** una fila suma 1.000000001 o cualquier valor fuera de la tolerancia de 1e-9
- **THEN** se lanza un ValueError que identifica el índice de la fila inválida

#### Scenario: ME-01-S4 valores fuera de rango rechazados

- **WHEN** la matriz contiene un valor negativo o mayor que 1
- **THEN** se lanza un ValueError que indica que las probabilidades deben estar entre 0 y 1

#### Scenario: ME-01-S5 menos de tres estados rechazados

- **WHEN** se valida una matriz de 2x2 o una lista de estados con menos de tres elementos
- **THEN** se lanza un ValueError que exige al menos tres estados

#### Scenario: ME-01-S6 estados duplicados o vacíos rechazados

- **WHEN** la lista de estados contiene nombres repetidos, vacíos o en blanco
- **THEN** se lanza un ValueError que exige estados únicos y no vacíos

### Requirement: ME-02 Potencias de la matriz de transición

El motor MUST calcular P^n para n entero no negativo, cumpliendo P^0 = identidad y P^1 = P.

#### Scenario: ME-02-S1 potencia uno

- **WHEN** se calcula P^1 con la matriz válida
- **THEN** el resultado es numéricamente igual a la matriz original

#### Scenario: ME-02-S2 potencia cero

- **WHEN** se calcula P^0 con la matriz válida
- **THEN** el resultado es la matriz identidad del mismo orden

#### Scenario: ME-02-S3 potencias superiores

- **WHEN** se calcula P^3
- **THEN** el resultado es el producto matricial P · P · P y cada fila sigue sumando 1

#### Scenario: ME-02-S4 pasos negativos rechazados

- **WHEN** se solicita una potencia con n negativo
- **THEN** se lanza un ValueError que indica que los pasos deben ser no negativos

### Requirement: ME-03 Distribución desde estado inicial

El motor MUST devolver la distribución en n pasos cuando se proporciona un estado inicial válido, usando π_0 = e_i.

#### Scenario: ME-03-S1 estado inicial único

- **WHEN** se pide la distribución a 3 pasos desde Soleado
- **THEN** se devuelve el vector e_Soleado · P^3, con longitud igual al número de estados y suma 1

#### Scenario: ME-03-S2 estado desconocido rechazado

- **WHEN** se solicita una predicción desde un estado que no está en la lista
- **THEN** se lanza un ValueError que enumera los estados válidos

#### Scenario: ME-03-S3 múltiples pasos

- **WHEN** se solicitan simultáneamente los pasos 1, 3, 5 y 10 desde un estado
- **THEN** se devuelve una distribución por cada paso solicitado, todas con suma 1

### Requirement: ME-04 Distribución desde vector inicial

El motor MUST aceptar un vector inicial propio y MUST devolver π_0 · P^n para los pasos solicitados.

#### Scenario: ME-04-S1 vector inicial válido

- **WHEN** se proporciona un vector no negativo de longitud igual al número de estados que suma 1
- **THEN** la distribución en n pasos es el producto π_0 · P^n y suma 1

#### Scenario: ME-04-S2 vector inválido rechazado

- **WHEN** el vector inicial tiene otra longitud, contiene negativos o no suma 1 dentro de 1e-9
- **THEN** se lanza un ValueError que explica la condición violada

### Requirement: ME-05 Distribución estacionaria

El motor MUST calcular una distribución estacionaria π que cumpla π·P = π y ∑π = 1.

#### Scenario: ME-05-S1 convergencia con n grande

- **WHEN** se calcula la distribución estacionaria con un número grande de pasos
- **THEN** el resultado es no negativo, suma 1 y la norma infinito de π·P − π es menor que 1e-9

#### Scenario: ME-05-S2 coincidencia con potencia elevada

- **WHEN** se compara la distribución estacionaria con π_0 · P^1000 para un π_0 arbitrario válido
- **THEN** ambas distribuciones coinciden dentro de la tolerancia de 1e-9
