import numpy as np
import pytest

from app.markov import (
    DEFAULT_MATRIX,
    DEFAULT_STATES,
    distribution,
    distributions_for_steps,
    evolution,
    matrix_power,
    stationary_distribution,
    validate_matrix,
    validate_states,
)


def test_ME_01_S1_matriz_valida_aceptada():
    result = validate_matrix(DEFAULT_MATRIX, DEFAULT_STATES)

    assert isinstance(result, np.ndarray)
    assert result.shape == (4, 4)
    assert result.dtype == np.float64


def test_ME_01_S2_matriz_no_cuadrada_rechazada():
    with pytest.raises(ValueError, match="cuadrada"):
        validate_matrix([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], ["A", "B", "C"])


def test_ME_01_S3_fila_que_no_suma_uno_rechazada():
    matrix = [list(row) for row in DEFAULT_MATRIX]
    matrix[2][0] += 1e-8

    with pytest.raises(ValueError, match="fila 2"):
        validate_matrix(matrix, DEFAULT_STATES)


def test_ME_01_S3_tolerancia_1e9_aceptada():
    matrix = [list(row) for row in DEFAULT_MATRIX]
    matrix[0][0] += 5e-10

    result = validate_matrix(matrix, DEFAULT_STATES)

    assert np.isclose(result[0].sum(), 1.0, atol=1e-9, rtol=0.0)


def test_ME_01_S4_valores_fuera_de_rango_rechazados():
    negative = [list(row) for row in DEFAULT_MATRIX]
    negative[1][2] = -0.05
    with pytest.raises(ValueError, match="entre 0 y 1"):
        validate_matrix(negative, DEFAULT_STATES)

    greater = [list(row) for row in DEFAULT_MATRIX]
    greater[1][2] = 1.2
    with pytest.raises(ValueError, match="entre 0 y 1"):
        validate_matrix(greater, DEFAULT_STATES)


def test_ME_01_S5_menos_de_tres_estados_rechazados():
    with pytest.raises(ValueError, match="al menos 3"):
        validate_matrix([[0.5, 0.5], [0.4, 0.6]], ["A", "B"])
    with pytest.raises(ValueError, match="al menos 3"):
        validate_states(["A", "B"])


def test_ME_01_S6_estados_duplicados_o_vacios_rechazados():
    with pytest.raises(ValueError, match="únicos"):
        validate_states(["A", "B", "A"])
    with pytest.raises(ValueError, match="vacíos"):
        validate_states(["A", "  ", "C"])


def test_ME_02_S1_potencia_uno_igual_a_matriz():
    matrix = validate_matrix(DEFAULT_MATRIX)

    assert np.allclose(matrix_power(matrix, 1), matrix)


def test_ME_02_S2_potencia_cero_igual_a_identidad():
    matrix = validate_matrix(DEFAULT_MATRIX)

    assert np.allclose(matrix_power(matrix, 0), np.eye(4))


def test_ME_02_S3_potencias_superiores():
    matrix = validate_matrix(DEFAULT_MATRIX)
    result = matrix_power(matrix, 3)

    assert np.allclose(result, matrix @ matrix @ matrix)
    assert np.allclose(result.sum(axis=1), 1.0)


def test_ME_02_S3_caso_manual_tres_estados():
    matrix = [
        [0.5, 0.3, 0.2],
        [0.2, 0.5, 0.3],
        [0.3, 0.2, 0.5],
    ]

    assert np.allclose(matrix_power(matrix, 2)[0], [0.37, 0.34, 0.29])


def test_ME_02_S4_pasos_negativos_rechazados():
    with pytest.raises(ValueError, match="no negativos"):
        matrix_power(DEFAULT_MATRIX, -1)


def test_ME_03_S1_estado_inicial_unico():
    result = distribution("Soleado", 3, DEFAULT_MATRIX, DEFAULT_STATES)

    expected = np.array([1.0, 0.0, 0.0, 0.0]) @ np.linalg.matrix_power(
        np.array(DEFAULT_MATRIX), 3
    )
    assert np.allclose(result, expected)
    assert np.isclose(result.sum(), 1.0)


def test_ME_03_S1_caso_manual_tres_estados():
    states = ["A", "B", "C"]
    matrix = [
        [0.5, 0.3, 0.2],
        [0.2, 0.5, 0.3],
        [0.3, 0.2, 0.5],
    ]

    result = distribution("A", 2, matrix, states)

    assert np.allclose(result, [0.37, 0.34, 0.29])


def test_ME_03_S2_estado_desconocido_rechazado():
    with pytest.raises(ValueError, match="Estados válidos"):
        distribution("Nevado", 1, DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_03_S3_multiples_pasos():
    result = distributions_for_steps(
        "Nublado", [1, 3, 5, 10], DEFAULT_MATRIX, DEFAULT_STATES
    )

    assert set(result) == {1, 3, 5, 10}
    assert all(np.isclose(vector.sum(), 1.0) for vector in result.values())


def test_ME_03_S3_evolucion_de_cero_a_diez():
    values = evolution("Tormenta", 10, DEFAULT_MATRIX, DEFAULT_STATES)

    assert values.shape == (11, 4)
    assert np.allclose(values[0], [0.0, 0.0, 0.0, 1.0])
    assert np.allclose(values.sum(axis=1), 1.0)


def test_ME_04_S1_vector_inicial_valido():
    vector = [0.2, 0.3, 0.4, 0.1]
    result = distribution(vector, 2, DEFAULT_MATRIX, DEFAULT_STATES)

    expected = np.array(vector) @ np.linalg.matrix_power(np.array(DEFAULT_MATRIX), 2)
    assert np.allclose(result, expected)
    assert np.isclose(result.sum(), 1.0)


def test_ME_04_S2_vector_invalido_rechazado():
    with pytest.raises(ValueError, match="elementos"):
        distribution([0.5, 0.5, 0.0], 1, DEFAULT_MATRIX, DEFAULT_STATES)
    with pytest.raises(ValueError, match="negativos"):
        distribution([1.2, -0.2, 0.0, 0.0], 1, DEFAULT_MATRIX, DEFAULT_STATES)
    with pytest.raises(ValueError, match="sumar 1"):
        distribution([0.1, 0.2, 0.3, 0.1], 1, DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_05_S1_convergencia_y_equilibrio():
    matrix = validate_matrix(DEFAULT_MATRIX, DEFAULT_STATES)
    result = stationary_distribution(matrix, states=DEFAULT_STATES)

    assert np.all(result >= -1e-12)
    assert np.isclose(result.sum(), 1.0)
    assert float(np.max(np.abs(result @ matrix - result))) < 1e-9


def test_ME_05_S2_coincidencia_con_potencia_elevada():
    matrix = validate_matrix(DEFAULT_MATRIX, DEFAULT_STATES)
    stationary = stationary_distribution(matrix)
    from_initial = distribution([0.1, 0.2, 0.3, 0.4], 1000, matrix)

    assert np.allclose(stationary, from_initial, atol=1e-9)


def test_ME_01_S2_matriz_no_numerica_rechazada():
    with pytest.raises(ValueError, match="números"):
        validate_matrix([["x", 0, 0], [0, 1, 0], [0, 0, 1]])


def test_ME_01_S2_matriz_unidimensional_rechazada():
    with pytest.raises(ValueError, match="bidimensional"):
        validate_matrix([1.0, 0.0, 0.0])


def test_ME_01_S5_filas_insuficientes_sin_estados_rechazadas():
    with pytest.raises(ValueError, match="al menos 3"):
        validate_matrix([[0.5, 0.5], [0.5, 0.5]])


def test_ME_01_S5_longitud_de_estados_distinta_rechazada():
    with pytest.raises(ValueError, match="no coincide"):
        validate_matrix(DEFAULT_MATRIX, ["A", "B", "C"])


def test_ME_01_S4_valores_no_finitos_rechazados():
    matrix = [list(row) for row in DEFAULT_MATRIX]
    matrix[0][0] = float("nan")

    with pytest.raises(ValueError, match="no finitos"):
        validate_matrix(matrix, DEFAULT_STATES)


def test_ME_02_S4_pasos_no_enteros_y_excesivos_rechazados():
    with pytest.raises(ValueError, match="enteros"):
        matrix_power(DEFAULT_MATRIX, 1.5)
    with pytest.raises(ValueError, match="no puede superar"):
        matrix_power(DEFAULT_MATRIX, 10_001)


def test_ME_04_S2_vector_no_numerico_rechazado():
    with pytest.raises(ValueError, match="números"):
        distribution(["x", 0, 0, 0], 1, DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_04_S2_vector_bidimensional_rechazado():
    with pytest.raises(ValueError, match="unidimensional"):
        distribution([[0.25] * 4], 1, DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_04_S2_vector_no_finito_rechazado():
    with pytest.raises(ValueError, match="no finitos"):
        distribution([float("nan"), 0.0, 0.0, 1.0], 1, DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_04_S2_longitud_distinta_a_la_matriz_rechazada():
    with pytest.raises(ValueError, match="debe tener 4 elementos"):
        distribution([1 / 3, 1 / 3, 1 / 3], 1, DEFAULT_MATRIX)


def test_ME_03_S2_estado_requiere_lista_de_estados():
    with pytest.raises(ValueError, match="Se requiere la lista"):
        distribution("Soleado", 1, DEFAULT_MATRIX)


def test_ME_03_S3_lista_de_pasos_vacia_rechazada():
    with pytest.raises(ValueError, match="no puede estar vacía"):
        distributions_for_steps("Soleado", [], DEFAULT_MATRIX, DEFAULT_STATES)


def test_ME_05_S1_pasos_cero_rechazado_en_estacionaria():
    with pytest.raises(ValueError, match="al menos un paso"):
        stationary_distribution(DEFAULT_MATRIX, steps=0)
