from pathlib import Path
import sys

# permite importar el calculo existente
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from pydantic import ValidationError
from backend.app.models import LPRequest, LPResponse
from backend.app.solver import solve_lp
from frontend.plotting import plot_model, add_level_animation

# configura la pagina y carga su estilo visual
ASSETS = Path(__file__).resolve().parent / "assets"
st.set_page_config(
    page_title="UPC - Grupo 2 | Programacion lineal", page_icon="📈", layout="wide"
)
st.markdown(
    "<style>" + (ASSETS / "style.css").read_text() + "</style>", unsafe_allow_html=True
)

# define los ejemplos con sus objetivos y restricciones
EXAMPLES = {
    "Produccion de mesas y sillas": dict(
        a=80.0,
        b=50.0,
        mode="max",
        label="Ganancia",
        unit="S/",
        name1="mesas",
        name2="sillas",
        unit1="unidades",
        unit2="unidades",
        rows=[
            (2.0, 1.0, "<=", 40.0, "Horas de corte"),
            (1.0, 2.0, "<=", 50.0, "Horas de acabado"),
        ],
    ),
    "Compra de materia prima": dict(
        a=40.0,
        b=60.0,
        mode="min",
        label="Costo",
        unit="S/",
        name1="materia prima A",
        name2="materia prima B",
        unit1="lotes",
        unit2="lotes",
        rows=[
            (2.0, 1.0, ">=", 20.0, "Requerimiento 1"),
            (1.0, 2.0, ">=", 25.0, "Requerimiento 2"),
        ],
    ),
    "Varias decisiones con el mismo resultado": dict(
        a=1.0,
        b=1.0,
        mode="max",
        label="Valor objetivo",
        unit="",
        name1="producto A",
        name2="producto B",
        unit1="unidades",
        unit2="unidades",
        rows=[(1.0, 1.0, "<=", 10.0, "Capacidad total")],
    ),
    "Mi propio problema": dict(
        a=1.0,
        b=1.0,
        mode="max",
        label="Resultado",
        unit="",
        name1="cantidad A",
        name2="cantidad B",
        unit1="unidades",
        unit2="unidades",
        rows=[],
    ),
}


# carga los datos del ejemplo y borra el resultado anterior
def load_example(name: str) -> None:
    data = EXAMPLES[name]
    for key, value in data.items():
        if key != "rows":
            st.session_state[key] = value
    st.session_state["non_negative"] = True
    st.session_state["constraints"] = [
        dict(zip(("a", "b", "operator", "c", "label"), row)) for row in data["rows"]
    ]
    st.session_state["revision"] = st.session_state.get("revision", 0) + 1
    st.session_state.pop("result", None)
    st.session_state.pop("model_json", None)


# el selector carga el ejemplo sin un segundo boton
if "academic_started" not in st.session_state:
    load_example(next(iter(EXAMPLES)))
    st.session_state["academic_started"] = True


# actualiza los datos al seleccionar otro ejemplo
def change_example() -> None:
    load_example(st.session_state["example"])


# muestra la cabecera y la imagen de presentacion
st.markdown(
    '<div class="brand"><strong>UPC - grupo 2</strong></div>',
    unsafe_allow_html=True,
)
hero_text, hero_image = st.columns([1, 1], gap="large", vertical_alignment="center")
with hero_text:
    st.markdown(
        '<div class="hero-tag">LABORATORIO DE DECISIONES</div>', unsafe_allow_html=True
    )
    st.title("Cada recurso cuenta.")
    st.markdown(
        '<p class="hero-note">Explora tus opciones, comprende tus limites y encuentra la mejor combinacion.</p><div class="chips"><span>Dos variables</span><span>Metodo grafico</span><span>Resultados comprobables</span></div>',
        unsafe_allow_html=True,
    )
with hero_image:
    st.image(str(ASSETS / "taller.png"), width="stretch")

# explica el recorrido sin ocupar espacio durante el uso normal
with st.expander("Como usar esta pagina"):
    step1, step2, step3 = st.columns(3)
    with step1:
        st.markdown("**1. Elige un ejemplo**")
        st.write("Comienza con un caso preparado o selecciona tu propio problema.")
    with step2:
        st.markdown("**2. Ingresa los datos**")
        st.write("Modifica el objetivo, los productos y los recursos disponibles.")
    with step3:
        st.markdown("**3. Calcula y analiza**")
        st.write("Revisa la respuesta, la region factible y la comprobacion matematica.")

st.selectbox(
    "Elige un punto de partida", list(EXAMPLES), key="example", on_change=change_example
)

# oculta ajustes que no se necesitan en cada uso
with st.expander("Personalizar productos y unidades"):
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Primer producto", key="name1")
        st.text_input("Unidad del primer producto", key="unit1")
    with col2:
        st.text_input("Segundo producto", key="name2")
        st.text_input("Unidad del segundo producto", key="unit2")
    col1, col2 = st.columns(2)
    col1.text_input("Nombre del objetivo", key="label")
    col2.text_input("Unidad del resultado", key="unit")
    st.checkbox("Cantidades no negativas", key="non_negative")
name1, name2 = st.session_state["name1"], st.session_state["name2"]
label, unit = st.session_state["label"], st.session_state["unit"]
unit1, unit2 = st.session_state["unit1"], st.session_state["unit2"]

# recoge los coeficientes y el tipo de optimizacion
st.subheader("01  Tu objetivo")
c1, c2, c3 = st.columns([1.1, 1, 1])
mode = c1.selectbox(
    "Quiero",
    ["max", "min"],
    key="mode",
    format_func=lambda item: (
        "Maximizar el resultado" if item == "max" else "Minimizar el resultado"
    ),
)
a = c2.number_input(f"{label} por {name1}", key="a")
b = c3.number_input(f"{label} por {name2}", key="b")

# una sola tabla sustituye los cuadros y botones de cada restriccion
st.subheader("02  Tus recursos")
st.caption(
    "Edita la tabla como una hoja de calculo, agrega recursos en la ultima fila."
)
relations = {"Como maximo": "<=", "Como minimo": ">=", "Exactamente": "="}
reverse = {value: key for key, value in relations.items()}
base_rows = [
    {
        "recurso": c["label"],
        "producto_1": c["a"],
        "producto_2": c["b"],
        "condicion": reverse[c["operator"]],
        "total": c["c"],
    }
    for c in st.session_state["constraints"]
]
# asegura que una tabla vacia conserve sus columnas
base = pd.DataFrame(
    base_rows, columns=["recurso", "producto_1", "producto_2", "condicion", "total"]
)
for column in ["producto_1", "producto_2", "total"]:
    base[column] = base[column].astype(float)
editor_key = f"resources_{st.session_state['revision']}"
edited = st.data_editor(
    base,
    key=editor_key,
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "recurso": st.column_config.TextColumn("Recurso", width="medium"),
        "producto_1": st.column_config.NumberColumn(
            f"Por {name1}", required=True, format="%.4g"
        ),
        "producto_2": st.column_config.NumberColumn(
            f"Por {name2}", required=True, format="%.4g"
        ),
        "condicion": st.column_config.SelectboxColumn(
            "Condicion", options=list(relations), required=True, default="Como maximo"
        ),
        "total": st.column_config.NumberColumn("Total", required=True, format="%.4g"),
    },
)

# convierte las filas completas en restricciones del modelo
rows, incomplete = [], False
for row in edited.to_dict("records"):
    if all(pd.isna(value) or value == "" for value in row.values()):
        continue
    if (
        any(pd.isna(row[key]) for key in ["producto_1", "producto_2", "total"])
        or row["condicion"] not in relations
    ):
        incomplete = True
        continue
    rows.append(
        dict(
            a=row["producto_1"],
            b=row["producto_2"],
            c=row["total"],
            operator=relations[row["condicion"]],
            label="" if pd.isna(row["recurso"]) else str(row["recurso"]),
        )
    )
if incomplete:
    st.warning(
        "Completa los numeros y la condicion de las filas nuevas, puedes escribir cero."
    )
    st.stop()
# valida los datos antes de calcular
try:
    problem = LPRequest(
        objective=dict(a=a, b=b, mode=mode, label=label, unit=unit),
        constraints=rows,
        non_negative=st.session_state["non_negative"],
        var_names=[name1, name2],
    )
except ValidationError:
    st.warning("Revisa los nombres y los datos, se permiten hasta 30 restricciones.")
    st.stop()
model_json = problem.model_dump_json()

# mantiene el calculo directo sin servidor adicional
if st.button("Calcular resultado", type="primary", width="stretch"):
    st.session_state.pop("result", None)
    try:
        result = solve_lp(problem)
        st.session_state["result"] = result.model_dump()
        st.session_state["model_json"] = model_json
        st.session_state["level"] = float(result.optimal_value or 0.0)
        coords = [abs(v) for p in result.vertices for v in (p.x, p.y)]
        if result.feasible_point:
            coords += [abs(v) for v in result.feasible_point]
        if result.optimal_point:
            coords += [abs(result.optimal_point.x), abs(result.optimal_point.y)]
        st.session_state["extent"] = 1.4 * max([10.0] + coords)
    except (ValueError, ArithmeticError):
        st.error("No se pudo calcular, revisa los valores o su escala.")

# muestra resultados solo cuando corresponden a los datos actuales
if "result" not in st.session_state:
    st.caption(
        "Modelo continuo de dos variables, las cantidades pueden ser fraccionarias."
    )
    st.stop()
if model_json != st.session_state.get("model_json"):
    st.info("Cambiaste los datos, vuelve a calcular para actualizar el resultado.")
    st.stop()
result = LPResponse.model_validate(st.session_state["result"])

st.divider()
# presenta el estado y las cantidades de la solucion
st.subheader("03  La mejor combinacion")
if result.status in ("infeasible", "error"):
    st.error(result.message)
    st.stop()
if result.status == "unbounded":
    st.warning(result.message)
else:
    p = result.optimal_point
    c1, c2, c3 = st.columns(3)
    c1.metric(name1, f"{p.x:.6g}", help=f"Cantidad en {unit1}")
    c2.metric(name2, f"{p.y:.6g}", help=f"Cantidad en {unit2}")
    c3.metric(label, f"{unit} {p.z:.6g}")
    st.write(
        f"Elige **{p.x:.6g} {unit1} de {name1}** y **{p.y:.6g} {unit2} de {name2}**, "
        f"para obtener {label.lower()} de **{unit} {p.z:.6g}** respetando tus limites."
    )
    if result.multiple_optima:
        st.info(
            "Esta es una de infinitas soluciones optimas, el conjunto dorado tiene el mismo resultado."
        )
    if not result.vertices:
        st.caption(result.message)

# reserva las tablas y el modelo para quien necesite comprobar el calculo
chart, evidence = st.tabs(["Grafica", "Comprobacion matematica"])
# dibuja la region factible y permite mover la recta objetivo
with chart:
    st.markdown(
        '<div class="context"><strong>Como leer la grafica:</strong> la zona azul contiene las combinaciones permitidas, los puntos son los vertices y la estrella marca una solucion optima.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Mover la recta objetivo y ajustar la vista"):
        extent = st.number_input("Alcance de los ejes", min_value=0.01, key="extent")
        if a or b:
            limit = float(
                max(
                    1.0,
                    (abs(a) + abs(b)) * extent,
                    abs(result.optimal_value or 0.0) * 1.2,
                )
            )
            if not -limit <= st.session_state.get("level", 0.0) <= limit:
                st.session_state["level"] = float(result.optimal_value or 0.0)
            if result.status == "optimal" and st.button("Volver al nivel optimo"):
                st.session_state["level"] = float(result.optimal_value)
            level = st.slider(f"Nivel de {label}", -limit, limit, key="level")
            st.latex(rf"{a:g}x_1 {b:+g}x_2={level:.6g}")
            st.caption(
                "Este control fija un nivel manual, la animacion recorre los niveles dentro de la grafica sin cambiar este control."
            )
        else:
            level = 0.0
            st.caption(
                "Objetivo constante, todos los puntos factibles tienen valor cero."
            )
    fig = plot_model(problem, result, level, extent)
    fig = add_level_animation(fig, problem, result, extent)
    fig.update_layout(
        paper_bgcolor="#fffaf0",
        plot_bgcolor="#fffdf7",
        font=dict(color="#16334a"),
        height=650,
    )
    st.caption(
        "Presiona Recorrer niveles en la grafica para observar como la recta llega al optimo, el valor animado aparece dentro del dibujo."
    )
    st.plotly_chart(
        fig, width="stretch", config={"scrollZoom": True, "displaylogo": False}
    )
    st.caption(
        "Azul, region factible · rojo, nivel objetivo · estrella, optimo · dorado, soluciones multiples"
    )
    st.caption(
        "La region puede continuar fuera de la ventana visible, sus bordes no son restricciones."
    )
# muestra las ecuaciones y la comprobacion de los resultados
with evidence:
    st.caption(f"x1 = {name1}, x2 = {name2}, Z = {label}")
    st.latex(rf"\operatorname{{{mode}}}\ Z={a:g}x_1 {b:+g}x_2")
    for row in problem.constraints:
        op = {"<=": r"\leq", ">=": r"\geq", "=": "="}[row.operator]
        st.latex(rf"{row.a:g}x_1 {row.b:+g}x_2 {op} {row.c:g}")
    st.latex(r"x_1,x_2\geq0" if problem.non_negative else r"x_1,x_2\in\mathbb{R}")
    if result.vertices:
        st.write("Vertices y valor objetivo")
        st.dataframe(
            [{"x1": v.x, "x2": v.y, "valor objetivo": v.z} for v in result.vertices],
            hide_index=True,
            width="stretch",
        )
    if result.status == "optimal":
        st.write("Comprobacion de restricciones")
        st.dataframe(
            [
                {
                    "restriccion": r["restriction"],
                    "calculado": r["left"],
                    "relacion": r["operator"],
                    "limite": r["right"],
                    "cumple": "si" if r["valid"] else "no",
                }
                for r in result.checks
            ],
            hide_index=True,
            width="stretch",
        )
        st.latex(rf"Z=({a:g})({p.x:.6g})+({b:g})({p.y:.6g})={p.z:.6g}")
    st.caption(
        "Variables continuas y tolerancia numerica, no redondees cantidades sin comprobar su factibilidad."
    )

# identifica el curso y el grupo al pie de la pagina
st.markdown(
    '<div class="footnote">UPC - grupo 2</div>',
    unsafe_allow_html=True,
)
