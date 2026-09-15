---
name: topografia-a-dxf
description: Convertir puntos topográficos de un CSV a un DXF básico con coordenadas XYZ, identificadores y cotas. Usar para demostraciones y dibujos simples de relevamientos.
---

# Topografía a DXF

Skill básico para que un asistente con ejecución de Python genere un DXF desde un CSV. No requiere claves, servicios externos ni conexión con Civil 3D. No incluye un conversor ejecutable: el asistente crea y ejecuta el código siguiendo estas instrucciones.

## Cómo usarlo

Copiar la carpeta `topografia-a-dxf` en la carpeta de skills del asistente. En Codex, usar `~/.codex/skills/topografia-a-dxf/SKILL.md` (en Windows, `~` representa la carpeta del usuario). También se puede adjuntar este archivo al chat y pedir que siga sus instrucciones.

Para generar archivos se necesita un entorno con Python y la biblioteca `ezdxf`. Si falta, instalarla en un entorno virtual y registrar la versión utilizada. No es necesario tener AutoCAD instalado para generar el archivo.

## Entrada

CSV UTF-8 separado por comas y con punto decimal:

```csv
id,este,norte,cota,descripcion
P1,1000.000,2000.000,100.250,Esquina
P2,1020.000,2000.000,100.400,Esquina
P3,1020.000,2010.000,100.550,Esquina
P4,1000.000,2010.000,100.300,Esquina
```

Estos cuatro puntos son ficticios. Representan un sistema local en metros; no tienen un EPSG asignado.

- `id`: identificador único y no vacío.
- `este`: coordenada X.
- `norte`: coordenada Y.
- `cota`: coordenada Z.
- `descripcion`: texto opcional; puede omitirse la columna.

Para otros CSV, identificar explícitamente columnas, separador y decimal antes de convertir. No intercambiar Este/Norte para ajustar visualmente un dibujo.

## Procedimiento para el asistente

1. Leer el CSV sin modificar el original. Confirmar unidades y sistema de coordenadas con la información disponible; consultar si faltan. Para la demo anterior ya están definidos.
2. Validar identificadores únicos, campos obligatorios y valores numéricos finitos. Informar número de fila y motivo de los errores; no descartar filas silenciosamente ni sustituir cotas faltantes por cero.
3. Conservar X, Y y Z originales, incluidos valores negativos. No reproyectar, desplazar al origen ni asignar un EPSG por suposición. Si la entrada está en grados, resolver la proyección antes de tratarla como un plano en metros.
4. Crear un DXF R2010 con `ezdxf` y unidades acordes con la entrada. Para metros, establecer `$INSUNITS = 6`.
5. Dibujar en espacio modelo:
   - Capa `TOPO_PUNTOS`: una entidad POINT por fila en (Este, Norte, Cota).
   - Capa `TOPO_IDS`: un TEXT con el identificador.
   - Capa `TOPO_COTAS`: un TEXT con la cota expresada con tres decimales.
   - Usar textos de altura 0.25 m para esta demo, con desplazamientos XY que separen identificador y cota del punto. Mantener la elevación original en los textos. Adaptar altura y desplazamientos cuando cambien las unidades o la escala.
6. No unir puntos por defecto. Si se solicita un contorno, usar el orden indicado y una polilínea 3D cuando deban conservarse las cotas. Cerrar solo cuando se pida; no repetir innecesariamente el primer vértice.
7. Guardar en una ruta de salida nueva. Si el archivo ya existe, elegir otro nombre o seguir la instrucción explícita del usuario sobre reemplazarlo.
8. Reabrir el DXF con `ezdxf`, ejecutar su auditoría y comprobar cantidad de puntos, capas y correspondencia XYZ contra el CSV. Reportar cualquier error o reparación. No afirmar que se comprobó visualmente en CAD si no se abrió allí.

## Entrega

Entregar el DXF y un resumen breve con cantidad de puntos, unidades, sistema de coordenadas declarado, capas y validaciones realizadas. Conservar el script usado junto al resultado para poder repetir la conversión. El DXF no garantiza conservar metadatos de CRS: anotarlos en el resumen.

Este flujo genera entidades CAD simples. No genera puntos COGO, superficies TIN ni curvas de nivel.

## Prompt para mostrar el uso

> Usá $topografia-a-dxf con los cuatro puntos ficticios incluidos en el skill. Creá demo_topografia.dxf en metros y coordenadas locales, con puntos, identificadores y cotas. No unas los puntos. Entregá el DXF, el script utilizado y un resumen de la validación.

Resultado esperado: 4 POINT, 4 TEXT de identificador y 4 TEXT de cota; extensión de puntos X=1000 a 1020, Y=2000 a 2010 y Z=100.250 a 100.550.

## Reutilización

Se permite copiar, adaptar y compartir este archivo para demostraciones y uso propio. El ejemplo no contiene relevamientos reales, datos personales, rutas privadas ni credenciales.
