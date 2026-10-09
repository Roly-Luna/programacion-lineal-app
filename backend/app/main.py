"""
Ejecutar con: uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import LPRequest, LPResponse
from .solver import solve_lp

app = FastAPI(
    title="LP Graphical Solver API",
    description="Resuelve problemas de Programacion Lineal con 2 variables mediante el metodo grafico.",
    version="1.0.0",
)

# CORS abierto para desarrollo local (Streamlit corre en otro puerto/proceso)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/solve", response_model=LPResponse)
def solve(request: LPRequest) -> LPResponse:
    """
    Recibe la funcion objetivo y las restricciones, y devuelve:
    - los vertices de la region factible
    - el punto optimo y el valor optimo de la funcion objetivo
    - segmentos de recta listos para graficar cada restriccion
    - el estado del problema: optimal | infeasible | unbounded
    """
    return solve_lp(request)
