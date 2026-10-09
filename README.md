# Proyecto de programacion lineal

Aplicacion web para resolver problemas de programacion lineal con dos variables mediante el metodo grafico. Permite ingresar la funcion objetivo y las restricciones, construir la region factible, evaluar sus vertices y mostrar una solucion optima.

## Funciones principales

- Resuelve problemas de maximizacion y minimizacion.
- Admite restricciones `<=`, `>=` e `=`.
- Grafica las restricciones y la region factible.
- Identifica los vertices y una solucion optima.
- Anima el desplazamiento de la recta objetivo.
- Comprueba que la solucion cumpla las restricciones.
- Incluye ejemplos listos para probar.

## Requisitos

- Conexion a internet durante la instalacion inicial.
- Git para clonar el repositorio.
- uv para instalar Python y las dependencias del proyecto.

No es necesario crear manualmente un entorno virtual ni ejecutar `uv init`. El proyecto ya contiene `pyproject.toml` y `uv.lock`.

## Instalacion en Windows

### 1. Instalar Git

Descarga Git desde <https://git-scm.com/download/win> y completa la instalacion con las opciones predeterminadas.

### 2. Instalar uv

Abre PowerShell y ejecuta:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra PowerShell, abre una ventana nueva y comprueba la instalacion:

```powershell
uv --version
```

### 3. Descargar el proyecto

```powershell
git clone https://github.com/Roly-Luna/proyecto-algebra-lineal.git
cd proyecto-algebra-lineal
```

### 4. Instalar Python y las dependencias

```powershell
uv python install 3.14
uv sync
```

### 5. Ejecutar la aplicacion

```powershell
uv run streamlit run frontend/streamlit_app.py
```

Streamlit mostrara una direccion local, normalmente <http://localhost:8501>. Si el navegador no se abre automaticamente, copia esa direccion y pegala en el navegador.

## Instalacion en macOS

### 1. Instalar Git

Abre Terminal y ejecuta:

```bash
git --version
```

Si Git no esta instalado, macOS mostrara una ventana para instalar las herramientas necesarias. Acepta la instalacion y vuelve a abrir Terminal.

### 2. Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cierra Terminal, abre una ventana nueva y comprueba la instalacion:

```bash
uv --version
```

### 3. Descargar el proyecto

```bash
git clone https://github.com/Roly-Luna/proyecto-algebra-lineal.git
cd proyecto-algebra-lineal
```

### 4. Instalar Python y las dependencias

```bash
uv python install 3.14
uv sync
```

### 5. Ejecutar la aplicacion

```bash
uv run streamlit run frontend/streamlit_app.py
```

Abre <http://localhost:8501> si la pagina no aparece automaticamente.

## Como usar la aplicacion

1. Selecciona un ejemplo o elige `Mi propio problema`.
2. Define los nombres y las unidades de las dos variables.
3. Selecciona maximizar o minimizar.
4. Ingresa los coeficientes de la funcion objetivo.
5. Agrega las restricciones en la tabla de recursos.
6. Presiona `Calcular resultado`.
7. Revisa la solucion, la grafica y la comprobacion matematica.

## Detener la aplicacion

Regresa a la terminal y presiona `Ctrl + C`.

## Estructura principal

```text
backend/app/models.py       modelos de entrada y salida
backend/app/solver.py       calculo matematico
frontend/streamlit_app.py   interfaz web
frontend/plotting.py        grafica y animacion
frontend/assets/            estilos e imagenes
pyproject.toml              dependencias del proyecto
uv.lock                     versiones exactas de las dependencias
```

## Problemas frecuentes

### El comando uv no existe

Cierra la terminal, abre una nueva y ejecuta `uv --version`. Si el problema continua, repite la instalacion de uv.

### El puerto 8501 esta ocupado

Ejecuta la aplicacion en otro puerto:

```bash
uv run streamlit run frontend/streamlit_app.py --server.port 8502
```

### Los resultados no cambian

Despues de modificar los datos, vuelve a presionar `Calcular resultado`.

## Integrantes

Grupo 2, Algebra Lineal, Universidad Peruana de Ciencias Aplicadas.
