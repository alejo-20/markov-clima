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
