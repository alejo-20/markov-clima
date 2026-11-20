from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

from app.markov import (
    DEFAULT_MATRIX,
    DEFAULT_STATES,
    MAX_STEPS,
    distributions_for_steps,
    evolution,
    stationary_distribution,
    validate_matrix,
    validate_states,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_STEPS = [1, 3, 5, 10]
DEFAULT_EVOLUTION_STEPS = 10


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    states: list[str] | None = None
    matrix: list[list[float]] | None = None
    initial_state: str | None = None
    initial_vector: list[float] | None = None
    steps: list[StrictInt] = Field(default_factory=lambda: list(DEFAULT_STEPS))
    include_evolution: bool = True
    max_evolution_step: StrictInt = DEFAULT_EVOLUTION_STEPS
    include_stationary: bool = False

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("La lista de pasos no puede estar vacía.")
        for step in value:
            if step < 0:
                raise ValueError(f"Los pasos deben ser enteros no negativos; recibió {step}.")
            if step > MAX_STEPS:
                raise ValueError(f"Los pasos no pueden superar {MAX_STEPS}; recibió {step}.")
        return value

    @field_validator("max_evolution_step")
    @classmethod
    def validate_max_evolution_step(cls, value: int) -> int:
        if value < 0 or value > MAX_STEPS:
            raise ValueError(
                f"max_evolution_step debe estar entre 0 y {MAX_STEPS}; recibió {value}."
            )
        return value

    @model_validator(mode="after")
    def validate_initial_input(self) -> PredictRequest:
        if self.initial_state is not None and self.initial_vector is not None:
            raise ValueError("Debe elegirse solo una opción: 'initial_state' o 'initial_vector'.")
        if self.initial_state is None and self.initial_vector is None:
            raise ValueError("Debe proporcionar 'initial_state' o 'initial_vector'.")
        return self


class ModelResponse(BaseModel):
    states: list[str]
    matrix: list[list[float]]


class PredictResponse(BaseModel):
    states: list[str]
    matrix: list[list[float]]
    steps: list[int]
    initial_state: str | None = None
    initial_vector: list[float] | None = None
    distributions: dict[str, list[float]]
    evolution: dict[str, list[float]] | None = None
    stationary: list[float] | None = None


app = FastAPI(
    title="Cadenas de Markov - Clima Bogotá",
    description="Predicción del clima diario con una cadena de Markov discreta.",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
        message = str(error.get("msg", "valor inválido"))
        messages.append(f"{location}: {message}" if location else message)
    detail = "Datos de petición inválidos. " + "; ".join(messages)
    return JSONResponse(status_code=422, content={"detail": detail})


@app.get("/api/model", response_model=ModelResponse)
def get_model() -> ModelResponse:
    return ModelResponse(
        states=list(DEFAULT_STATES),
        matrix=[list(row) for row in DEFAULT_MATRIX],
    )


@app.post("/api/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        states = validate_states(payload.states) if payload.states is not None else list(DEFAULT_STATES)
        matrix = validate_matrix(
            payload.matrix if payload.matrix is not None else DEFAULT_MATRIX,
            states,
        )
        initial = (
            payload.initial_state.strip()
            if payload.initial_state is not None
            else payload.initial_vector
        )
        distributions = distributions_for_steps(initial, payload.steps, matrix, states)

        evolution_values: dict[str, list[float]] | None = None
        if payload.include_evolution:
            values = evolution(initial, payload.max_evolution_step, matrix, states)
            evolution_values = {
                states[index]: [float(value) for value in values[:, index]]
                for index in range(len(states))
            }

        stationary_values: list[float] | None = None
        if payload.include_stationary:
            stationary_values = [
                float(value) for value in stationary_distribution(matrix, states=states)
            ]

        return PredictResponse(
            states=states,
            matrix=matrix.tolist(),
            steps=list(payload.steps),
            initial_state=payload.initial_state,
            initial_vector=payload.initial_vector,
            distributions={
                str(step): [float(value) for value in vector]
                for step, vector in distributions.items()
            },
            evolution=evolution_values,
            stationary=stationary_values,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
