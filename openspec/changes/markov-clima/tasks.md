# Tasks

## 1. Entorno y estructura

- [x] 1.1 Crear requirements.txt con FastAPI, Uvicorn, NumPy, pytest, httpx y pytest-cov; crear y activar el entorno virtual `venv` e instalar dependencias
- [x] 1.2 Crear la estructura `app/`, `app/static/` y `tests/` respetando el .gitignore

## 2. Motor de Markov (ME-01 a ME-05)

- [ ] 2.1 Implementar en `app/markov.py` la validación de estados y matriz con tolerancia 1e-9 (ME-01)
- [ ] 2.2 Implementar el cálculo de P^n, incluyendo P^0 = I y P^1 = P (ME-02)
- [ ] 2.3 Implementar distribuciones desde estado inicial y desde vector inicial para varios pasos (ME-03, ME-04)
- [ ] 2.4 Implementar la distribución estacionaria y la comprobación π·P = π (ME-05)

## 3. API (API-01 a API-03)

- [ ] 3.1 Definir modelos Pydantic, constantes del modelo por defecto y manejo de errores 422 (API-03)
- [ ] 3.2 Implementar GET /api/model (API-01)
- [ ] 3.3 Implementar POST /api/predict con estado o vector, pasos y matriz opcional (API-02)
- [ ] 3.4 Montar los archivos estáticos y el endpoint raíz que sirve la UI

## 4. Interfaz web (UI-01 a UI-03)

- [ ] 4.1 Crear `app/static/index.html` con selector de estado, tabla editable, botón Calcular, contenedores de gráficas, tabla de resultados y área de errores (UI-01, UI-02, UI-03)
- [ ] 4.2 Crear `app/static/styles.css` con diseño claro, en español y responsive (UI-03-S2)
- [ ] 4.3 Crear `app/static/app.js` con validación local, llamada a la API, gráficas Chart.js de barras agrupadas y líneas 0..10, referencia estacionaria, tabla a 4 decimales y mensajes de error (UI-01-S2, UI-02, UI-03-S1)

## 5. Pruebas automatizadas

- [ ] 5.1 Crear `tests/test_markov.py` con pruebas nombradas por requisito/escenario: matrices válidas e inválidas, P^0, P^1, suma 1, caso de 3 estados calculado a mano, vector inicial y estacionaria (ME-01 a ME-05)
- [ ] 5.2 Crear `tests/test_api.py` con pruebas nombradas por requisito/escenario para éxito y errores 422 de todos los escenarios API (API-01 a API-03)
- [ ] 5.3 Añadir una prueba por cada Scenario de UI-01 a UI-03 que verifique el HTML/JS/CSS entregado y ejecutar `pytest -v --cov=app`, reportando la cobertura

## 6. Cierre y evidencia

- [ ] 6.1 Crear README.md con problema, fundamento matemático, matriz y estados, instalación, ejecución, pruebas, estructura, flujo SDD/OpenSpec y uso de opencode
- [ ] 6.2 Verificar el arranque con `uvicorn app.main:app --reload` y comprobar que las gráficas se renderizan
- [ ] 6.3 Ejecutar `openspec archive markov-clima` y verificar que los requisitos pasan a `openspec/specs/`
- [ ] 6.4 Hacer push final a GitHub y entregar URL y checklist de cumplimiento
