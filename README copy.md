# Optima, segunda entrega

## Ejecutar

Descomprime la carpeta y abre una terminal dentro de entrega2-academica

```bash
uv sync
uv run streamlit run frontend/streamlit_app.py
```

No hace falta iniciar FastAPI, la interfaz llama directamente al solver

## Como usar

Elige un ejemplo, cambia los coeficientes o recursos y presiona Calcular resultado

La tabla permite agregar filas y eliminar las seleccionadas, utiliza Como maximo para <=, Como minimo para >= y Exactamente para =

En la grafica, Recorrer niveles anima la recta hasta el optimo y Pausar detiene el recorrido, el nivel animado aparece dentro del dibujo, el control manual esta en el desplegable sobre la grafica y conserva su propio valor

La pestana Comprobacion matematica muestra el modelo, los vertices y la verificacion de las restricciones

## Archivos

- frontend/streamlit_app.py, interfaz
- frontend/plotting.py, grafica y animacion
- frontend/assets/style.css, tipografia y colores
- frontend/assets/taller.png, ilustracion contextual generada para el proyecto
- .streamlit/config.toml, tema claro
- backend/app/models.py, validacion
- backend/app/solver.py, calculo geometrico y comprobacion con scipy
- backend/app/main.py, API opcional que la interfaz actual no utiliza

Si actualizas una version anterior copia las carpetas frontend, backend y .streamlit de este paquete, conserva las rutas de las imagenes y estilos

## Alcance para la entrega

Incluye region factible, vertices, optimo, interpretacion, movimiento de la recta, soluciones multiples y comprobaciones numericas

La rubrica tambien exige informe, diagrama, capturas explicadas y conclusiones, esos entregables deben completarse aparte

Se utilizan variables continuas, no se resuelven problemas de programacion entera, las tolerancias numericas pueden requerir reformular datos de escalas extremas

La imagen es ilustrativa, la grafica y los resultados se calculan con los datos ingresados, la identificacion UPC aparece como texto y no como un logo oficial

## Pruebas

```bash
uv run python -m unittest discover -s tests -v
```

Se verificaron 12 casos del solver y 2 pruebas de interfaz y animacion, muebles da 1800 y materia prima da 800, la animacion termina en el nivel optimo
