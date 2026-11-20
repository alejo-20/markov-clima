from __future__ import annotations

from collections.abc import Sequence

import numpy as np

TOLERANCE = 1e-9
MIN_STATES = 3
MAX_STEPS = 10_000
STATIONARY_STEPS = 1_000

DEFAULT_STATES: list[str] = ["Soleado", "Nublado", "Lluvioso", "Tormenta"]

DEFAULT_MATRIX: list[list[float]] = [
    [0.50, 0.30, 0.18, 0.02],
    [0.25, 0.35, 0.35, 0.05],
    [0.15, 0.35, 0.40, 0.10],
    [0.10, 0.30, 0.45, 0.15],
]

MatrixLike = Sequence[Sequence[float]] | np.ndarray


def validate_states(states: Sequence[str]) -> list[str]:
    if len(states) < MIN_STATES:
        raise ValueError(f"Se requieren al menos {MIN_STATES} estados; recibió {len(states)}.")

    cleaned = [str(state).strip() for state in states]
    if any(not state for state in cleaned):
        raise ValueError("Los estados no pueden estar vacíos ni contener solo espacios.")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Los estados deben ser únicos; hay nombres repetidos.")
    return cleaned


def validate_matrix(matrix: MatrixLike, states: Sequence[str] | None = None) -> np.ndarray:
    expected_states = validate_states(states) if states is not None else None

    try:
        result = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("La matriz debe contener solo números y tener filas de la misma longitud.") from exc

    if result.ndim != 2:
        raise ValueError("La matriz debe ser bidimensional.")

    rows, cols = result.shape
    if rows != cols:
        raise ValueError(f"La matriz debe ser cuadrada; recibió {rows}x{cols}.")
    if rows < MIN_STATES:
        raise ValueError(f"Se requieren al menos {MIN_STATES} estados; recibió {rows}.")
    if expected_states is not None and len(expected_states) != rows:
        raise ValueError(f"La matriz de {rows}x{cols} no coincide con los {len(expected_states)} estados.")
    if not np.all(np.isfinite(result)):
        raise ValueError("La matriz no puede contener valores no finitos (NaN o infinito).")
    if np.any(result < 0.0) or np.any(result > 1.0):
        raise ValueError("Todas las probabilidades de la matriz deben estar entre 0 y 1.")

    for index, total in enumerate(result.sum(axis=1)):
        if not np.isclose(total, 1.0, atol=TOLERANCE, rtol=0.0):
            raise ValueError(
                f"La fila {index} suma {total:.12f} en lugar de 1 (tolerancia {TOLERANCE:g})."
            )

    return result


def _validate_step_count(steps: int) -> int:
    if isinstance(steps, bool) or not isinstance(steps, int):
        raise ValueError("Los pasos deben ser enteros no negativos.")
    if steps < 0:
        raise ValueError(f"Los pasos deben ser no negativos; recibió {steps}.")
    if steps > MAX_STEPS:
        raise ValueError(f"El número de pasos no puede superar {MAX_STEPS}; recibió {steps}.")
    return steps


def matrix_power(matrix: MatrixLike, steps: int) -> np.ndarray:
    validated = validate_matrix(matrix)
    count = _validate_step_count(steps)
    return np.linalg.matrix_power(validated, count)


def validate_initial_vector(vector: Sequence[float] | np.ndarray, states: Sequence[str] | None = None) -> np.ndarray:
    expected_states = validate_states(states) if states is not None else None

    try:
        result = np.asarray(vector, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("El vector inicial debe contener solo números.") from exc

    if result.ndim != 1:
        raise ValueError("El vector inicial debe ser unidimensional.")
    if expected_states is not None and result.size != len(expected_states):
        raise ValueError(
            f"El vector inicial debe tener {len(expected_states)} elementos; recibió {result.size}."
        )
    if result.size < MIN_STATES:
        raise ValueError(f"Se requieren al menos {MIN_STATES} estados; recibió {result.size}.")
    if not np.all(np.isfinite(result)):
        raise ValueError("El vector inicial no puede contener valores no finitos (NaN o infinito).")
    if np.any(result < 0.0):
        raise ValueError("El vector inicial no puede contener valores negativos.")
    if not np.isclose(result.sum(), 1.0, atol=TOLERANCE, rtol=0.0):
        raise ValueError(f"El vector inicial debe sumar 1 (recibió {result.sum():.12f}).")
    return result


def initial_distribution(
    initial: str | Sequence[float] | np.ndarray,
    states: Sequence[str] | None = None,
) -> np.ndarray:
    if isinstance(initial, str):
        if states is None:
            raise ValueError("Se requiere la lista de estados para usar un estado inicial.")
        resolved = validate_states(states)
        if initial not in resolved:
            raise ValueError(
                f"El estado '{initial}' no existe. Estados válidos: {', '.join(resolved)}."
            )
        vector = np.zeros(len(resolved), dtype=float)
        vector[resolved.index(initial)] = 1.0
        return vector
    return validate_initial_vector(initial, states)


def _prepare_distribution_inputs(
    initial: str | Sequence[float] | np.ndarray,
    matrix: MatrixLike,
    states: Sequence[str] | None,
) -> tuple[np.ndarray, np.ndarray]:
    resolved = validate_states(states) if states is not None else None
    validated = validate_matrix(matrix, resolved)
    vector = initial_distribution(initial, resolved)
    if vector.size != validated.shape[0]:
        raise ValueError(
            f"El vector inicial debe tener {validated.shape[0]} elementos; recibió {vector.size}."
        )
    return vector, validated


def distribution(
    initial: str | Sequence[float] | np.ndarray,
    steps: int,
    matrix: MatrixLike,
    states: Sequence[str] | None = None,
) -> np.ndarray:
    vector, validated = _prepare_distribution_inputs(initial, matrix, states)
    count = _validate_step_count(steps)
    return vector @ np.linalg.matrix_power(validated, count)


def distributions_for_steps(
    initial: str | Sequence[float] | np.ndarray,
    steps: Sequence[int],
    matrix: MatrixLike,
    states: Sequence[str] | None = None,
) -> dict[int, np.ndarray]:
    counts = list(steps)
    if not counts:
        raise ValueError("La lista de pasos no puede estar vacía.")
    return {count: distribution(initial, count, matrix, states) for count in counts}


def evolution(
    initial: str | Sequence[float] | np.ndarray,
    max_steps: int,
    matrix: MatrixLike,
    states: Sequence[str] | None = None,
) -> np.ndarray:
    vector, validated = _prepare_distribution_inputs(initial, matrix, states)
    count = _validate_step_count(max_steps)
    values = np.empty((count + 1, validated.shape[0]), dtype=float)
    current = vector.copy()
    for step in range(count + 1):
        values[step] = current
        current = current @ validated
    return values
