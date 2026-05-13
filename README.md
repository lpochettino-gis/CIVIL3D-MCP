# Civil 3D MCP

Servidor MCP local para controlar AutoCAD Civil 3D desde un chat compatible con Model Context Protocol.

El servidor usa COM via `pywin32`, por lo que debe ejecutarse en Windows con AutoCAD/Civil 3D abierto en la misma sesion de usuario.

## Herramientas incluidas

- `civil3d_ping`: verifica la conexion con AutoCAD/Civil 3D.
- `civil3d_drawing_info`: devuelve nombre, ruta, estado de guardado y unidades del dibujo activo.
- `civil3d_run_command`: ejecuta comandos de AutoCAD/Civil 3D.
- `civil3d_list_entities`: lista entidades del espacio modelo.
- `civil3d_get_alignments`: lista alineaciones Civil 3D.
- `civil3d_get_alignment_stations`: obtiene puntos XY sobre una alineacion.
- `civil3d_list_surfaces`: lista superficies TIN o Grid.
- `civil3d_get_surface_elevation`: consulta elevacion de superficie en XY.
- `civil3d_generate_grid_txt`: exporta grilla XYZ desde una superficie.
- `civil3d_run_python`: ejecuta Python local con acceso a COM.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecucion

1. Abrir AutoCAD Civil 3D.
2. Abrir o crear un dibujo.
3. Ejecutar:

```powershell
.\.venv\Scripts\python.exe -u .\server.py
```

Tambien se puede usar `run_server.bat` desde esta carpeta.

## Configuracion MCP

Ejemplo para clientes MCP:

```json
{
  "mcpServers": {
    "civil3d": {
      "command": "C:\\ruta\\civil3d-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-u", "C:\\ruta\\civil3d-mcp\\server.py"],
      "env": {}
    }
  }
}
```

Reemplazar `C:\\ruta\\civil3d-mcp` por la ruta local donde se clone el repositorio.

## Seguridad

Este MCP controla una aplicacion local abierta y puede modificar el dibujo activo. Revisar los comandos antes de ejecutarlos y evitar exponer el servidor fuera de `localhost`.

`civil3d_run_python` ejecuta codigo Python arbitrario en la maquina local. Usarlo solo con prompts y usuarios de confianza.

