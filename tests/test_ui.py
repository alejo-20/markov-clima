from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.markov import DEFAULT_STATES

STATIC_DIR = Path(__file__).resolve().parents[1] / "app" / "static"
client = TestClient(app)


def test_UI_01_S1_carga_inicial_muestra_controles():
    response = client.get("/")
    html = response.text

    assert response.status_code == 200
    for marker in ('id="initial-state"', 'id="matrix-body"', 'id="calculate-btn"'):
        assert marker in html
    for state in DEFAULT_STATES:
        assert state in html


def test_UI_01_S2_matriz_invalida_se_valida_localmente():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="error-message"' in html
    assert "readMatrixFromDOM" in script
    assert "1e-9" in script
    assert "no es numérico" in script
    assert "cada fila debe sumar 1" in script


def test_UI_01_S3_matriz_editada_se_envia_a_la_api():
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert 'fetch("/api/predict"' in script
    assert "matrix: matrix" in script

    matrix = [
        [0.5, 0.3, 0.2],
        [0.2, 0.5, 0.3],
        [0.3, 0.2, 0.5],
    ]
    response = client.post(
        "/api/predict",
        json={
            "states": ["A", "B", "C"],
            "matrix": matrix,
            "initial_state": "A",
            "steps": [2],
        },
    )

    assert response.status_code == 200
    assert response.json()["distributions"]["2"][0] == pytest.approx(0.37)


def test_UI_02_S1_graficas_y_tabla_tras_calcular():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="chart-bars"' in html
    assert 'id="chart-lines"' in html
    assert 'id="results-body"' in html
    assert script.count("new Chart") >= 2
    assert 'type: "bar"' in script
    assert 'type: "line"' in script
    assert "HORIZONS = [1, 3, 5, 10]" in script
    assert "MAX_EVOLUTION_STEP = 10" in script
    assert ".toFixed(4)" in script


def test_UI_02_S2_referencia_estacionaria_opcional():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="include-stationary"' in html
    assert "payload.stationary" in script
    assert "Estacionaria" in script


def test_UI_03_S1_error_de_api_visible():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'role="alert"' in html
    assert "response.ok" in script
    assert "errorBox.textContent" in script
    assert "No se pudo calcular" in script


def test_UI_03_S2_diseno_responsive_y_en_espanol():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    css = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")

    assert 'lang="es"' in html
    assert "@media (max-width: 768px)" in css
    assert "overflow-x: auto" in css


def test_UI_01_S1_respuesta_alternativa_sin_index(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.STATIC_DIR", tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "próximamente" in response.text
