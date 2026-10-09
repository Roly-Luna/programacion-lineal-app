from itertools import combinations
import numpy as np
from scipy.optimize import linprog
from .models import LPRequest, LPResponse, VertexOut

TOL = 1e-7


# convierte las restricciones a filas normalizadas
# cada fila representa a por x mas b por y menor o igual a c
# las igualdades se conservan por separado

def rows_for(problem):
    inequalities, equalities = [], []
    for item in problem.constraints:
        row = np.array([item.a, item.b, item.c], dtype=float)
        scale = max(abs(item.a), abs(item.b))
        if scale:
            row /= scale
        if item.operator == '=':
            equalities.append(row)
        else:
            inequalities.append(-row if item.operator == '>=' else row)
    return inequalities, equalities


def feasible(point, inequalities, equalities):
    return all(np.dot(r[:2], point) <= r[2] + TOL * (1 + abs(r[2])) for r in inequalities) and all(
        abs(np.dot(r[:2], point) - r[2]) <= TOL * (1 + abs(r[2])) for r in equalities
    )


# calcula el optimo y verifica casos sin vertices o sin limite

def solve_lp(problem: LPRequest) -> LPResponse:
    inequalities, equalities = rows_for(problem)
    objective = np.array([problem.objective.a, problem.objective.b], dtype=float)
    objective_scale = max(abs(objective)) or 1.0
    scaled_objective = objective / objective_scale
    bounds = [(0, None), (0, None)] if problem.non_negative else [(None, None)] * 2

    def optimize(cost, extra_equalities=()):
        eq = equalities + list(extra_equalities)
        return linprog(
            cost,
            A_ub=[r[:2] for r in inequalities] or None,
            b_ub=[r[2] for r in inequalities] or None,
            A_eq=[r[:2] for r in eq] or None,
            b_eq=[r[2] for r in eq] or None,
            bounds=bounds, method='highs',
        )

    feasibility = optimize([0, 0])
    if feasibility.status == 2:
        return LPResponse(status='infeasible', message='No existe una combinacion que cumpla todas las restricciones.')
    if not feasibility.success:
        return LPResponse(status='error', message='No fue posible verificar el modelo, revise la escala de los datos.')

    # incorpora los ejes solo si la no negatividad forma parte del modelo
    geometry_inequalities = list(inequalities)
    if problem.non_negative:
        geometry_inequalities += [np.array([-1., 0., 0.]), np.array([0., -1., 0.])]
    candidates = []
    for first, second in combinations(geometry_inequalities + equalities, 2):
        matrix = np.array([first[:2], second[:2]])
        if abs(np.linalg.det(matrix)) < 1e-12:
            continue
        point = np.linalg.solve(matrix, [first[2], second[2]])
        if feasible(point, geometry_inequalities, equalities) and not any(
            np.allclose(point, old, atol=TOL, rtol=1e-9) for old in candidates
        ):
            candidates.append(point)
    if candidates:
        center = np.mean(candidates, axis=0)
        candidates.sort(key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0]))

    def vertex(point):
        return VertexOut(x=float(point[0]), y=float(point[1]), z=float(objective @ point))

    vertices = [vertex(point) for point in candidates]
    sense = -1 if problem.objective.mode == 'max' else 1
    optimum = optimize(sense * scaled_objective)
    shared = dict(vertices=vertices, feasible_point=feasibility.x.tolist())
    if optimum.status == 3:
        return LPResponse(status='unbounded', message='El objetivo puede mejorar sin limite, no existe un optimo finito.', **shared)
    if not optimum.success:
        return LPResponse(status='error', message='No fue posible calcular el optimo de forma fiable.', **shared)

    # compara los vertices y contrasta el resultado con un optimizador independiente
    selected = optimum.x
    z = float(objective @ selected)
    if candidates:
        values = [float(objective @ p) for p in candidates]
        index = int(np.argmax(values) if sense == -1 else np.argmin(values))
        if not np.isclose(values[index], z, atol=1e-6, rtol=1e-7):
            return LPResponse(status='error', message='La comprobacion del optimo no coincide, revise el modelo.', **shared)
        selected = candidates[index]
        z = values[index]

    # busca puntos distintos con el mismo valor objetivo
    # permite reconocer segmentos optimos y conjuntos optimos no acotados
    face = [np.array([*scaled_objective, z / objective_scale])] if np.any(objective) else []
    optimal_points = [selected]
    face_unbounded = False
    for cost in ([1, 0], [-1, 0], [0, 1], [0, -1]):
        result = optimize(cost, face)
        if result.status == 3:
            face_unbounded = True
        elif result.success:
            if not any(np.allclose(result.x, old, atol=1e-6, rtol=1e-8) for old in optimal_points):
                optimal_points.append(result.x)
        else:
            return LPResponse(status='error', message='No fue posible verificar si el optimo es unico.', **shared)
    multiple = face_unbounded or len(optimal_points) > 1

    # verifica cada restriccion con los valores originales
    checks = []
    for i, item in enumerate(problem.constraints):
        left = item.a * selected[0] + item.b * selected[1]
        epsilon = TOL * (1 + abs(left) + abs(item.c))
        ok = (left <= item.c + epsilon if item.operator == '<=' else
              left >= item.c - epsilon if item.operator == '>=' else abs(left - item.c) <= epsilon)
        checks.append(dict(restriction=item.label or f'Restriccion {i + 1}', left=float(left),
                           operator=item.operator, right=item.c, valid=bool(ok),
                           active=bool(abs(left - item.c) <= epsilon)))
    if problem.non_negative:
        for name, value in zip(problem.var_names, selected):
            checks.append(dict(restriction=f'{name} no negativa', left=float(value), operator='>=',
                               right=0., valid=bool(value >= -TOL), active=bool(abs(value) <= TOL)))
    valid = all(check['valid'] for check in checks) and feasible(selected, geometry_inequalities, equalities)
    if not valid:
        return LPResponse(status='error', message='El resultado no supero la validacion numerica.', **shared)
    message = 'Existen infinitas soluciones optimas.' if multiple else 'Se encontro una solucion optima unica.'
    if not candidates:
        message += ' Este conjunto no tiene vertices, el optimo se obtuvo mediante comprobacion lineal.'
    return LPResponse(status='optimal', message=message, optimal_point=vertex(selected),
                      optimal_value=z, multiple_optima=multiple, optimal_face_unbounded=face_unbounded,
                      optimal_points=[vertex(p) for p in optimal_points], checks=checks, validated=True, **shared)
