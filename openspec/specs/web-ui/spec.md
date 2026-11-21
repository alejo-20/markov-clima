# web-ui Specification

## Purpose

Esta capacidad describe la interfaz web en español que permite configurar el modelo, ejecutar simulaciones y visualizar los resultados de forma comprensible y adaptable a distintos tamaños de pantalla.

## Requirements

### Requirement: UI-01 Configuración del modelo

La interfaz MUST permitir seleccionar el estado inicial y editar la matriz de transición, validando las filas antes de calcular.

#### Scenario: UI-01-S1 carga inicial

- **WHEN** se abre la página principal
- **THEN** se muestran el selector con los cuatro estados, la tabla editable de la matriz y un botón Calcular

#### Scenario: UI-01-S2 matriz inválida en la UI

- **WHEN** el usuario modifica una celda de modo que su fila no sume 1 o escribe un valor no numérico
- **THEN** se muestra un mensaje de error en español y no se envía la petición de cálculo

#### Scenario: UI-01-S3 matriz válida reutilizada

- **WHEN** el usuario corrige la fila y vuelve a calcular
- **THEN** la petición usa la matriz editada y los resultados se actualizan

### Requirement: UI-02 Visualización de resultados

La interfaz MUST mostrar gráficas de barras agrupadas y de líneas, además de una tabla numérica con cuatro decimales.

#### Scenario: UI-02-S1 gráficas y tabla tras calcular

- **WHEN** el usuario pulsa Calcular y la API responde correctamente
- **THEN** se muestra un gráfico de barras agrupadas por estado en los pasos 1, 3, 5 y 10, un gráfico de líneas de 0 a 10 pasos y una tabla con valores a 4 decimales

#### Scenario: UI-02-S2 distribución estacionaria opcional

- **WHEN** el usuario activa la opción de referencia estacionaria
- **THEN** se añade una referencia visual de la distribución estacionaria a las gráficas o a la tabla

### Requirement: UI-03 Errores y adaptabilidad

La interfaz MUST mostrar errores de forma clara y MUST mantener una presentación legible en pantallas pequeñas.

#### Scenario: UI-03-S1 error de la API visible

- **WHEN** la API devuelve un error 422 o la petición falla por red
- **THEN** se muestra el mensaje de error en un área dedicada y no se sobrescriben los últimos resultados válidos

#### Scenario: UI-03-S2 diseño responsive

- **WHEN** la página se abre en un viewport móvil
- **THEN** los controles, tablas y gráficas se reorganizan sin desbordamiento horizontal y el texto permanece en español
