from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator


# define los datos de una restriccion
class ConstraintIn(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    a: float
    b: float
    operator: Literal['<=', '>=', '=']
    c: float
    label: str = ''


# define los datos de la funcion objetivo
class ObjectiveIn(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    a: float
    b: float
    mode: Literal['max', 'min'] = 'max'
    label: str = 'Ganancia'
    unit: str = 'S/'


# valida la entrada del problema
class LPRequest(BaseModel):
    objective: ObjectiveIn
    constraints: list[ConstraintIn] = Field(default_factory=list, max_length=30)
    non_negative: bool = True
    var_names: list[str] = Field(default_factory=lambda: ['x1', 'x2'], min_length=2, max_length=2)

    @model_validator(mode='after')
    def validate_names(self):
        self.var_names = [name.strip() for name in self.var_names]
        if not all(self.var_names) or self.var_names[0] == self.var_names[1]:
            raise ValueError('Ingrese dos nombres diferentes y no vacios')
        return self


# representa un punto y su valor objetivo
class VertexOut(BaseModel):
    x: float
    y: float
    z: float


# devuelve resultados y evidencia de validacion
class LPResponse(BaseModel):
    status: Literal['optimal', 'infeasible', 'unbounded', 'error']
    message: str
    vertices: list[VertexOut] = Field(default_factory=list)
    optimal_point: VertexOut | None = None
    optimal_value: float | None = None
    multiple_optima: bool = False
    optimal_face_unbounded: bool = False
    optimal_points: list[VertexOut] = Field(default_factory=list)
    feasible_point: list[float] | None = None
    checks: list[dict] = Field(default_factory=list)
    validated: bool = False
