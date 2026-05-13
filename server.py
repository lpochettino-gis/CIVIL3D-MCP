import json
import pythoncom
import win32com.client
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("civil3d-mcp")


def _acad():
    """Obtiene la instancia activa de AutoCAD via COM."""
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("AutoCAD.Application")
    except Exception as e:
        raise RuntimeError(f"AutoCAD no está abierto o no responde: {e}")


@mcp.tool()
def civil3d_ping() -> str:
    """Verifica la conexión con AutoCAD Civil 3D."""
    acad = _acad()
    return f"Conectado a AutoCAD {acad.Version} — Dibujo activo: {acad.ActiveDocument.Name}"


@mcp.tool()
def civil3d_drawing_info() -> str:
    """Devuelve información del dibujo activo: nombre, ruta, estado de guardado y unidades."""
    acad = _acad()
    doc = acad.ActiveDocument
    info = {
        "nombre": doc.Name,
        "ruta": doc.FullName,
        "guardado": doc.Saved,
        "unidades_insercion": doc.GetVariable("INSUNITS"),
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


@mcp.tool()
def civil3d_run_command(command: str) -> str:
    """
    Ejecuta un comando de AutoCAD o Civil 3D en el dibujo activo.

    Args:
        command: Comando a ejecutar (ej: 'ZOOM E', 'REGEN', 'AECCALIGNMENTCREATE').
    """
    acad = _acad()
    acad.ActiveDocument.SendCommand(command + "\n")
    return f"Comando ejecutado: {command}"


@mcp.tool()
def civil3d_list_entities(type_filter: str = "") -> str:
    """
    Lista entidades en el espacio modelo con filtro opcional por tipo.

    Args:
        type_filter: Fragmento del tipo a filtrar (ej: 'AeccDb', 'LINE', 'LWPOLYLINE'). Vacío = todos.
    """
    acad = _acad()
    ms = acad.ActiveDocument.ModelSpace
    entities = []
    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            etype = e.EntityName
            if not type_filter or type_filter.lower() in etype.lower():
                entities.append({
                    "index": i,
                    "tipo": etype,
                    "handle": e.Handle,
                    "capa": e.Layer,
                })
        except Exception:
            continue
    return json.dumps(entities, ensure_ascii=False, indent=2)


@mcp.tool()
def civil3d_get_alignments() -> str:
    """Lista todas las alineaciones Civil 3D del dibujo con sus datos de estacionamiento."""
    acad = _acad()
    ms = acad.ActiveDocument.ModelSpace
    alignments = []
    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            if "AeccDbAlignment" not in e.EntityName:
                continue
            a = {
                "nombre": e.Name,
                "handle": e.Handle,
                "capa": e.Layer,
            }
            try:
                a["longitud_m"] = round(e.Length, 3)
                a["inicio_est"] = round(e.StartingStation, 3)
                a["fin_est"] = round(e.EndingStation, 3)
            except Exception:
                pass
            alignments.append(a)
        except Exception:
            continue

    if not alignments:
        return "No se encontraron alineaciones (AeccDbAlignment) en el espacio modelo."
    return json.dumps(alignments, ensure_ascii=False, indent=2)


@mcp.tool()
def civil3d_get_alignment_stations(alignment_name: str, interval: float = 10.0) -> str:
    """
    Obtiene coordenadas XY cada N metros a lo largo de una alineación Civil 3D.
    Pensado para cálculo de pendientes en ductos y análisis de traza.

    Args:
        alignment_name: Nombre exacto de la alineación (case-sensitive).
        interval: Intervalo de muestreo en metros (default: 10.0).
    """
    acad = _acad()
    ms = acad.ActiveDocument.ModelSpace

    target = None
    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            if "AeccDbAlignment" in e.EntityName and e.Name == alignment_name:
                target = e
                break
        except Exception:
            continue

    if target is None:
        return f"No se encontró alineación con nombre: '{alignment_name}'"

    try:
        start = target.StartingStation
        end = target.EndingStation
        stations = []
        sta = start
        while sta <= end + 1e-6:
            try:
                pt = target.GetPointAtStation(sta)
                stations.append({
                    "estacion": round(sta, 3),
                    "x": round(pt[0], 3),
                    "y": round(pt[1], 3),
                })
            except Exception as ex:
                stations.append({"estacion": round(sta, 3), "error": str(ex)})
            sta += interval

        # Punto final exacto si no quedó cubierto
        if stations and abs(stations[-1]["estacion"] - end) > 0.1:
            try:
                pt = target.GetPointAtStation(end)
                stations.append({"estacion": round(end, 3), "x": round(pt[0], 3), "y": round(pt[1], 3)})
            except Exception:
                pass

        return json.dumps(stations, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al obtener estaciones: {e}"


@mcp.tool()
def civil3d_get_surface_elevation(surface_name: str, x: float, y: float) -> str:
    """
    Obtiene la elevación de una superficie Civil 3D en un punto XY dado.
    Útil para cálculo de cobertura de ductos.

    Args:
        surface_name: Nombre exacto de la superficie.
        x: Coordenada X en unidades del dibujo.
        y: Coordenada Y en unidades del dibujo.
    """
    acad = _acad()
    ms = acad.ActiveDocument.ModelSpace

    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            if not any(t in e.EntityName for t in ("AeccDbTinSurface", "AeccDbGridSurface", "AeccDbSurfaceTin")):
                continue
            if e.Name != surface_name:
                continue
            elev = e.FindElevationAtXY(x, y)
            return json.dumps({
                "superficie": surface_name,
                "x": x,
                "y": y,
                "elevacion_m": round(elev, 3),
            }, ensure_ascii=False, indent=2)
        except Exception as ex:
            return f"Error al consultar superficie '{surface_name}': {ex}"

    return f"No se encontró superficie con nombre: '{surface_name}'"


@mcp.tool()
def civil3d_list_surfaces() -> str:
    """Lista todas las superficies TIN o Grid del dibujo."""
    acad = _acad()
    ms = acad.ActiveDocument.ModelSpace
    surfaces = []
    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            etype = e.EntityName
            if any(t in etype for t in ("AeccDbTinSurface", "AeccDbGridSurface", "AeccDbSurfaceTin")):
                surfaces.append({
                    "nombre": e.Name,
                    "tipo": etype,
                    "capa": e.Layer,
                    "handle": e.Handle,
                })
        except Exception:
            continue
    if not surfaces:
        return "No se encontraron superficies en el dibujo."
    return json.dumps(surfaces, ensure_ascii=False, indent=2)


@mcp.tool()
def civil3d_generate_grid_txt(surface_name: str, interval: float = 10.0, output_dir: str = "") -> str:
    """
    Genera una grilla de puntos XYZ cada N metros sobre una superficie Civil 3D
    y la guarda como TXT. Formato: X Y Z por línea.

    Args:
        surface_name: Nombre exacto de la superficie.
        interval: Espaciado de la grilla en metros (default: 10.0).
        output_dir: Carpeta de destino. Si vacío, usa la misma carpeta del DWG.
    """
    import os

    acad = _acad()
    doc = acad.ActiveDocument
    ms = doc.ModelSpace

    surface = None
    for i in range(ms.Count):
        try:
            e = ms.Item(i)
            if any(t in e.EntityName for t in ("AeccDbTinSurface", "AeccDbGridSurface", "AeccDbSurfaceTin")):
                if e.Name == surface_name:
                    surface = e
                    break
        except Exception:
            continue

    if surface is None:
        return f"No se encontró superficie con nombre: '{surface_name}'"

    try:
        ext_min = surface.GetBoundingBox()[0]
        ext_max = surface.GetBoundingBox()[1]
        x_min, y_min = ext_min[0], ext_min[1]
        x_max, y_max = ext_max[0], ext_max[1]
    except Exception as ex:
        return f"Error al obtener extensión de la superficie: {ex}"

    if not output_dir:
        dwg_path = doc.FullName
        output_dir = os.path.dirname(dwg_path) if dwg_path else os.path.expanduser("~")

    output_dir = os.path.join(output_dir, "grilla_civil3d")
    os.makedirs(output_dir, exist_ok=True)

    safe_name = surface_name.replace(" ", "_").replace("/", "-")
    output_file = os.path.join(output_dir, f"grilla_{safe_name}_{int(interval)}m.txt")

    puntos_ok = 0
    puntos_err = 0

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("X\tY\tZ\n")
        x = x_min
        while x <= x_max + 1e-6:
            y = y_min
            while y <= y_max + 1e-6:
                try:
                    z = surface.FindElevationAtXY(x, y)
                    f.write(f"{round(x, 3)}\t{round(y, 3)}\t{round(z, 3)}\n")
                    puntos_ok += 1
                except Exception:
                    puntos_err += 1
                y += interval
            x += interval

    return json.dumps({
        "archivo": output_file,
        "superficie": surface_name,
        "intervalo_m": interval,
        "puntos_generados": puntos_ok,
        "puntos_fuera_superficie": puntos_err,
        "extension": {
            "x_min": round(x_min, 3), "x_max": round(x_max, 3),
            "y_min": round(y_min, 3), "y_max": round(y_max, 3),
        }
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def civil3d_run_python(code: str) -> str:
    """
    Ejecuta código Python arbitrario en el proceso del servidor MCP.
    Tiene acceso a win32com, pythoncom y la instancia activa de AutoCAD.
    Define la variable 'result' (str) en el código para retornar un valor.
    """
    import io
    import contextlib

    acad = _acad()
    doc = acad.ActiveDocument
    ms = doc.ModelSpace

    namespace = {
        "acad": acad,
        "doc": doc,
        "ms": ms,
        "win32com": win32com.client,
        "pythoncom": pythoncom,
        "json": json,
        "result": None,
    }

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(code, namespace)  # noqa: S102
        except Exception as ex:
            import traceback
            print(f"ERROR: {ex}\n{traceback.format_exc()}")

    output = buf.getvalue()
    explicit = namespace.get("result")
    return str(explicit) if explicit is not None else (output or "OK — sin output")


if __name__ == "__main__":
    mcp.run()
