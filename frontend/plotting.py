import numpy as np
import plotly.graph_objects as go
from backend.app.solver import rows_for


# recorta un poligono con un semiplano
# el rectangulo inicial es una ventana de dibujo y no una restriccion real


def clip(polygon, row):
    if not polygon:
        return []
    output = []
    for start, end in zip(polygon, polygon[1:] + polygon[:1]):
        ds = float(np.dot(row[:2], start) - row[2])
        de = float(np.dot(row[:2], end) - row[2])
        inside_start, inside_end = ds <= 1e-9, de <= 1e-9
        if inside_start != inside_end:
            t = ds / (ds - de)
            output.append(np.array(start) + t * (np.array(end) - start))
        if inside_end:
            output.append(np.array(end))
    return output


# calcula donde una recta cruza los bordes de la ventana
def line_points(a, b, c, box):
    xmin, xmax, ymin, ymax = box
    points = []
    if abs(b) > 1e-14:
        points.extend([(x, (c - a * x) / b) for x in (xmin, xmax)])
    if abs(a) > 1e-14:
        points.extend([((c - b * y) / a, y) for y in (ymin, ymax)])
    valid = []
    for point in points:
        if (
            xmin - 1e-7 <= point[0] <= xmax + 1e-7
            and ymin - 1e-7 <= point[1] <= ymax + 1e-7
        ):
            if not any(np.allclose(point, p, atol=1e-8) for p in valid):
                valid.append(point)
    return valid[:2]


def plot_bounds(problem, extent):
    # deja un margen pequeno para que los ejes y los puntos no se corten
    low = -0.045 * extent if problem.non_negative else -extent
    return (low, extent, low, extent)


# construye la grafica del modelo y sus resultados
def plot_model(problem, result, level, extent):
    box = plot_bounds(problem, extent)
    xmin, xmax, ymin, ymax = box
    polygon = [
        np.array(p, dtype=float)
        for p in [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    ]
    # recorta la ventana con todas las restricciones
    inequalities, equalities = rows_for(problem)
    if problem.non_negative:
        inequalities = list(inequalities) + [
            np.array([-1.0, 0.0, 0.0]),
            np.array([0.0, -1.0, 0.0]),
        ]
    for row in inequalities:
        polygon = clip(polygon, row)
    for row in equalities:
        polygon = clip(clip(polygon, row), -row)
    # sombrea la parte visible de la region factible
    fig = go.Figure()
    if polygon and result.status not in ("infeasible", "error"):
        closed = polygon + [polygon[0]]
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p in closed],
                y=[p[1] for p in closed],
                mode="lines",
                fill="toself",
                fillcolor="rgba(40,140,190,0.18)",
                line=dict(color="#2384ad", width=3),
                name="Conjunto factible visible",
            )
        )
    # dibuja las rectas de las restricciones
    for i, con in enumerate(problem.constraints):
        pts = line_points(con.a, con.b, con.c, box)
        if len(pts) == 2:
            fig.add_trace(
                go.Scatter(
                    x=[p[0] for p in pts],
                    y=[p[1] for p in pts],
                    mode="lines",
                    name=f'R{i+1}: {con.label or "restriccion"}',
                    line=dict(width=2.4),
                )
            )
    # marca los vertices y sus coordenadas
    if result.vertices:
        fig.add_trace(
            go.Scatter(
                x=[v.x for v in result.vertices],
                y=[v.y for v in result.vertices],
                customdata=[v.z for v in result.vertices],
                mode="markers+text",
                name="Vertices factibles",
                text=[f"({v.x:.4g}, {v.y:.4g})" for v in result.vertices],
                textposition="top right",
                textfont=dict(size=13, color="#18394f"),
                cliponaxis=False,
                marker=dict(size=10, color="#18394f"),
                hovertemplate="x=%{x:.4g}<br>y=%{y:.4g}<br>objetivo=%{customdata:.5g}<extra></extra>",
            )
        )
    # dibuja la recta objetivo en el nivel seleccionado
    obj = problem.objective
    pts = line_points(obj.a, obj.b, level, box)
    if len(pts) == 2:
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p in pts],
                y=[p[1] for p in pts],
                mode="lines",
                name=f"{obj.label}, nivel {level:.5g}",
                line=dict(color="#bc284a", width=3.5, dash="dash"),
            )
        )
    # resalta la solucion y el conjunto de optimos cuando existe
    if result.status == "optimal":
        if result.multiple_optima and polygon:
            if obj.a == 0 and obj.b == 0:
                face = polygon
            else:
                row = np.array([obj.a, obj.b, result.optimal_value], dtype=float)
                row /= max(abs(obj.a), abs(obj.b))
                face = clip(clip(polygon, row), -row)
            if face:
                fig.add_trace(
                    go.Scatter(
                        x=[p[0] for p in face],
                        y=[p[1] for p in face],
                        mode="lines",
                        line=dict(width=7, color="#d39b18"),
                        name="Conjunto optimo visible",
                    )
                )
        point = result.optimal_point
        fig.add_trace(
            go.Scatter(
                x=[point.x],
                y=[point.y],
                mode="markers",
                name=(
                    "Una solucion optima"
                    if result.multiple_optima
                    else "Solucion optima"
                ),
                marker=dict(size=15, color="#bc284a", symbol="star"),
            )
        )
    # conserva los limites elegidos sin expandirlos por la relacion de aspecto
    # las escalas se leen en los ejes y no se fuerza un cuadrado en pantalla
    axis_style = dict(
        autorange=False,
        showgrid=True,
        gridcolor="#dfe5e5",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#18394f",
        zerolinewidth=2.5,
        showline=True,
        linecolor="#aab8bf",
        ticks="outside",
        tickfont=dict(size=13, color="#294959"),
        automargin=True,
        nticks=8,
    )
    fig.update_layout(
        template="plotly_white",
        height=620,
        dragmode="pan",
        xaxis=dict(
            **axis_style,
            title=dict(
                text=f"x1 · {problem.var_names[0]}",
                font=dict(size=17, color="#18394f"),
                standoff=14,
            ),
            range=[xmin, xmax],
        ),
        yaxis=dict(
            **axis_style,
            title=dict(
                text=f"x2 · {problem.var_names[1]}",
                font=dict(size=17, color="#18394f"),
                standoff=14,
            ),
            range=[ymin, ymax],
        ),
        legend=dict(orientation="h", y=-0.2, font=dict(size=12)),
        margin=dict(l=70, r=35, t=40, b=145),
        hovermode="closest",
        annotations=[
            dict(
                x=0.99,
                y=0.99,
                xref="paper",
                yref="paper",
                text=f"nivel = {level:.5g}",
                showarrow=False,
                xanchor="right",
                bgcolor="#fffaf0",
                font=dict(color="#b84535", size=13),
            )
        ],
    )
    return fig


# anima la recta sin cambiar el problema ni sus restricciones
# termina en el nivel optimo y permite detener el recorrido


def add_level_animation(fig, problem, result, extent):
    if result.status != "optimal" or not (problem.objective.a or problem.objective.b):
        return fig
    obj = problem.objective
    target = next(
        (
            i
            for i, trace in enumerate(fig.data)
            if trace.name.startswith(f"{obj.label}, nivel")
        ),
        None,
    )
    region = next(
        (trace for trace in fig.data if trace.name == "Conjunto factible visible"), None
    )
    if target is None or region is None:
        return fig
    values = [obj.a * x + obj.b * y for x, y in zip(region.x, region.y)]
    if not values:
        return fig
    start = min(values) if obj.mode == "max" else max(values)
    finish = result.optimal_value
    box = plot_bounds(problem, extent)
    frames = []
    for i, level in enumerate(np.linspace(start, finish, 30)):
        points = line_points(obj.a, obj.b, float(level), box)
        # permite visualizar el contacto en una esquina de la ventana
        if len(points) == 1:
            points = points * 2
        if len(points) == 2:
            frames.append(
                go.Frame(
                    name=str(i),
                    traces=[target],
                    data=[
                        go.Scatter(
                            x=[p[0] for p in points],
                            y=[p[1] for p in points],
                            name=f"{obj.label}, nivel {level:.5g}",
                        )
                    ],
                    layout=go.Layout(
                        annotations=[
                            dict(
                                x=0.99,
                                y=0.99,
                                xref="paper",
                                yref="paper",
                                text=f"nivel = {level:.5g}",
                                showarrow=False,
                                xanchor="right",
                                bgcolor="#fffaf0",
                                font=dict(color="#b84535"),
                            )
                        ]
                    ),
                )
            )
    fig.frames = frames
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0,
                y=-0.25,
                xanchor="left",
                yanchor="top",
                showactive=False,
                bgcolor="#fffaf0",
                buttons=[
                    dict(
                        label="▶ Recorrer niveles",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=100, redraw=False),
                                transition=dict(duration=0),
                                fromcurrent=False,
                                mode="immediate",
                            ),
                        ],
                    ),
                    dict(
                        label="Pausar",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                transition=dict(duration=0),
                                mode="immediate",
                            ),
                        ],
                    ),
                ],
            )
        ],
        margin=dict(l=70, r=35, t=40, b=175),
        legend=dict(orientation="h", y=-0.12),
    )
    return fig
