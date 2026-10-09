# Proyecto de programacion lineal

Esta guia supone que Visual Studio Code y Git ya estan instalados.

## 1. Abrir la terminal de Visual Studio Code

Abre Visual Studio Code y, en el menu superior, selecciona:

```text
Terminal > New Terminal
```

## 2. Instalar uv en Windows

Si utilizas Windows, copia este comando en la terminal de Visual Studio Code y presiona `Enter`:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cuando termine, cierra completamente Visual Studio Code y vuelve a abrirlo.

Abre otra vez `Terminal > New Terminal` y comprueba la instalacion:

```powershell
uv --version
```

## 3. Instalar uv en macOS

Si utilizas macOS, copia este comando en la terminal de Visual Studio Code y presiona `Enter`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cuando termine, cierra completamente Visual Studio Code y vuelve a abrirlo.

Abre otra vez `Terminal > New Terminal` y comprueba la instalacion:

```bash
uv --version
```

## 4. Clonar el proyecto

1. Presiona `Ctrl + Shift + P` en Windows o `Cmd + Shift + P` en macOS.
2. Escribe `Git: Clone`.
3. Selecciona **Git: Clone**.
4. Pega este enlace:

```text
https://github.com/Roly-Luna/proyecto-algebra-lineal.git
```

5. Presiona `Enter`.
6. Selecciona la carpeta donde guardaras el proyecto.
7. Espera a que termine la descarga.
8. Cuando aparezca la pregunta para abrir el repositorio, presiona **Open**.
9. Si aparece una pregunta de confianza, confirma que confias en los autores.

## 5. Instalar Python y las dependencias

Con el proyecto abierto, selecciona:

```text
Terminal > New Terminal
```

Ejecuta estos comandos:

```bash
uv python install 3.14
uv sync
```

No ejecutes `uv init`. El proyecto ya contiene `pyproject.toml` y `uv.lock`.

## 6. Ejecutar la aplicacion

En la misma terminal, ejecuta:

```bash
uv run streamlit run frontend/streamlit_app.py
```

La aplicacion se abrira automaticamente en el navegador.

Si no se abre, visita:

```text
http://localhost:8501
```

Para detener la aplicacion, regresa a la terminal y presiona `Ctrl + C`.

## 7. Descargar futuras actualizaciones

Cuando el proyecto sea actualizado en GitHub:

1. Abre la carpeta del proyecto en Visual Studio Code.
2. Presiona `Ctrl + Shift + P` en Windows o `Cmd + Shift + P` en macOS.
3. Escribe `Git: Pull`.
4. Selecciona **Git: Pull**.
5. Abre `Terminal > New Terminal`.
6. Ejecuta:

```bash
uv sync
uv run streamlit run frontend/streamlit_app.py
```

## Uso de la aplicacion

1. Selecciona un ejemplo o elige `Mi propio problema`.
2. Ingresa la funcion objetivo y las restricciones.
3. Presiona `Calcular resultado`.
4. Revisa la solucion, la grafica y la comprobacion matematica.