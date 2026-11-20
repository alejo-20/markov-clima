import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.markov import DEFAULT_STATES

client = TestClient(app)


def test_API_01_S1_modelo_por_defecto():
    response = client.get("/api/model")

    assert response.status_code == 200
    data = response.json()
    assert data["states"] == DEFAULT_STATES
    assert len(data["matrix"]) == 4
    assert all(len(row) == 4 for row in data["matrix"])
    assert all(sum(row) == pytest.approx(1.0) for row in data["matrix"])


def test_API_02_S1_prediccion_desde_estado_inicial():
    response = client.post(
        "/api/predict",
        json={"initial_state": "Lluvioso", "steps": [1, 3, 5, 10]},
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data["distributions"]) == {"1", "3", "5", "10"}
    assert all(len(vector) == 4 for vector in data["distributions"].values())
    assert all(sum(vector) == pytest.approx(1.0) for vector in data["distributions"].values())


def test_API_02_S2_prediccion_desde_vector_inicial():
    response = client.post(
        "/api/predict",
        json={"initial_vector": [0.1, 0.2, 0.3, 0.4], "steps": [1, 2]},
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data["distributions"]) == {"1", "2"}
    assert all(sum(vector) == pytest.approx(1.0) for vector in data["distributions"].values())


def test_API_02_S3_matriz_personalizada():
    states = ["A", "B", "C"]
    matrix = [
        [0.5, 0.3, 0.2],
        [0.2, 0.5, 0.3],
        [0.3, 0.2, 0.5],
    ]
    response = client.post(
        "/api/predict",
        json={
            "states": states,
            "matrix": matrix,
            "initial_state": "A",
            "steps": [2],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["states"] == states
    assert all(actual == pytest.approx(expected) for actual, expected in zip(data["matrix"], matrix))
    assert data["distributions"]["2"] == pytest.approx([0.37, 0.34, 0.29])


def test_API_02_S4_evolucion_y_estacionaria():
    response = client.post(
        "/api/predict",
        json={
            "initial_state": "Soleado",
            "steps": [1, 3, 5, 10],
            "include_evolution": True,
            "include_stationary": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["stationary"] is not None
    assert sum(data["stationary"]) == pytest.approx(1.0)
    assert set(data["evolution"]) == set(DEFAULT_STATES)
    assert all(len(values) == 11 for values in data["evolution"].values())
    assert data["evolution"]["Soleado"][0] == pytest.approx(1.0)
    assert data["evolution"]["Lluvioso"][0] == pytest.approx(0.0)
    for index, state in enumerate(DEFAULT_STATES):
        assert data["evolution"][state][-1] == pytest.approx(
            data["distributions"]["10"][index], abs=1e-12
        )


def test_API_03_S1_estado_desconocido_devuelve_422():
    response = client.post(
        "/api/predict",
        json={"initial_state": "Nevado", "steps": [1]},
    )

    assert response.status_code == 422
    assert "Estados válidos" in response.json()["detail"]


def test_API_03_S2_pasos_invalidos_devuelven_422():
    negative = client.post(
        "/api/predict",
        json={"initial_state": "Soleado", "steps": [-1]},
    )
    empty = client.post(
        "/api/predict",
        json={"initial_state": "Soleado", "steps": []},
    )
    non_integer = client.post(
        "/api/predict",
        json={"initial_state": "Soleado", "steps": [1.5]},
    )

    assert negative.status_code == 422
    assert "pasos" in negative.json()["detail"]
    assert empty.status_code == 422
    assert "pasos" in empty.json()["detail"]
    assert non_integer.status_code == 422
    assert "steps" in non_integer.json()["detail"]


def test_API_03_S3_matriz_invalida_devuelve_422():
    bad_sum = [list(row) for row in client.get("/api/model").json()["matrix"]]
    bad_sum[0][0] = 0.6
    negative_value = [list(row) for row in client.get("/api/model").json()["matrix"]]
    negative_value[1][2] = -0.1

    sum_response = client.post(
        "/api/predict",
        json={"initial_state": "Soleado", "steps": [1], "matrix": bad_sum},
    )
    value_response = client.post(
        "/api/predict",
        json={"initial_state": "Soleado", "steps": [1], "matrix": negative_value},
    )

    assert sum_response.status_code == 422
    assert "fila 0" in sum_response.json()["detail"]
    assert value_response.status_code == 422
    assert "entre 0 y 1" in value_response.json()["detail"]


def test_API_03_S4_entrada_mutuamente_excluyente_devuelve_422():
    response = client.post(
        "/api/predict",
        json={
            "initial_state": "Soleado",
            "initial_vector": [0.25, 0.25, 0.25, 0.25],
            "steps": [1],
        },
    )

    assert response.status_code == 422
    assert "solo una opción" in response.json()["detail"]


def test_API_03_S5_sin_entrada_inicial_devuelve_422():
    response = client.post("/api/predict", json={"steps": [1]})

    assert response.status_code == 422
    assert "Debe proporcionar" in response.json()["detail"]
