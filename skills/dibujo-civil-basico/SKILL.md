---
name: dibujo-civil-basico
description: Crear croquis civiles 2D editables en DXF a partir de medidas, notas o bocetos, con capas, cotas y textos legibles. Usar para esquemas simples de plataformas, veredas y detalles geométricos en AutoCAD o Civil 3D.
---

# Dibujo civil básico

Convertir una descripción o croquis en un dibujo CAD editable y fácil de revisar. Adaptación básica del flujo de dibujo técnico: inventariar, definir geometría, dibujar por capas y verificar.

Este archivo contiene instrucciones para un asistente; no incluye un programa ejecutable. Para generar el DXF, el asistente necesita ejecución de Python y una biblioteca como `ezdxf`, o acceso a una aplicación CAD. No requiere claves ni servicios externos para la generación local.

## Cómo usarlo

Copiar esta carpeta en el directorio de skills del asistente o adjuntar este archivo al chat y pedir que siga sus instrucciones.

Aportar medidas, unidades y una descripción de qué se quiere dibujar. Si se usa una imagen, distinguir medidas escritas de proporciones estimadas: una foto por sí sola no permite obtener dimensiones reales.

## Datos mínimos

- Elementos a representar y medidas conocidas.
- Unidades del modelo.
- Origen y orientación, cuando deban coincidir con un plano existente.
- Formato solicitado: DXF por defecto; DWG solo si hay una herramienta de conversión disponible.

Para un esquema independiente sin ubicación real, se puede usar un origen local (0, 0), dejándolo declarado. No asignar coordenadas geográficas ni un sistema de referencia por suposición.

## Flujo de dibujo

1. **Inventariar.** Enumerar contornos, aberturas, ejes, cotas, títulos y notas. Conservar códigos originales y señalar cualquier texto ilegible.
2. **Resolver la geometría.** Trabajar a tamaño real, 1:1, en espacio modelo. Si falta una medida que determina la forma, consultarla; si solo se pide un esquema, identificar las partes sin dimensionar.
3. **Organizar capas.** Usar las necesarias de esta base:

   | Capa | Contenido |
   |---|---|
   | CIV-CONTORNO | Bordes y geometría principal |
   | CIV-EJES | Ejes de referencia |
   | CIV-COTAS | Cotas y líneas auxiliares |
   | CIV-TEXTO | Títulos y rótulos |
   | CIV-NOTAS | Unidades, supuestos y aclaraciones |

4. **Generar el DXF.** Preferir polilíneas cerradas para contornos y entidades DIMENSION para cotas editables. Si se usa `ezdxf`, renderizar las cotas para generar su representación gráfica. No dibujar únicamente el texto de una medida como si fuera una cota.
5. **Dar formato.** Colocar las cotas fuera de la geometría, separar textos y evitar superposiciones. Usar propiedades por capa. Adaptar alturas de texto al tamaño del dibujo y a su uso.
6. **Declarar unidades y escala.** Configurar las unidades del DXF según la entrada. Un modelo 1:1 no implica una escala de impresión definida; anotar “ESCALA DE IMPRESIÓN NO DEFINIDA” si no se preparó una lámina a escala. Para un croquis sin medidas reales, anotar “ESQUEMA SIN ESCALA”.
7. **Guardar y verificar.** Conservar el original y usar una salida nueva salvo indicación de reemplazo. Reabrir el DXF, comprobar medidas, cierre de contornos, capas y entidades. Ejecutar la auditoría disponible e informar errores o reparaciones.
8. **Revisar visualmente.** Abrir o renderizar el dibujo cuando haya herramientas disponibles, comprobando cotas, símbolos y textos. Si no se hizo, decirlo expresamente.

No deducir espesores estructurales, armaduras, pendientes de proyecto ni cumplimiento normativo a partir de un croquis. Este skill representa la geometría aportada; no realiza cálculo ni aprobación de ingeniería.

## Demo ficticia

Dibujar una plataforma rectangular de 12 × 8 metros en coordenadas locales, con Z=0:

| Vértice | X (m) | Y (m) |
|---|---:|---:|
| A | 0 | 0 |
| B | 12 | 0 |
| C | 12 | 8 |
| D | 0 | 8 |

- Contorno cerrado A-B-C-D, sin duplicar el primer vértice.
- Un eje horizontal de (0, 4) a (12, 4).
- Un eje vertical de (6, 0) a (6, 8).
- Cota horizontal de 12 m debajo del contorno.
- Cota vertical de 8 m a la derecha del contorno.
- Título: “PLATAFORMA — EJEMPLO DIDÁCTICO”.
- Nota: “Unidades: metros. Coordenadas locales. Escala de impresión no definida”.
- Altura inicial de texto: 0.25 m, ajustable para evitar solapamientos.

No agregar espesores, fundaciones ni datos de una obra real.

### Prompt listo para copiar

> Usá $dibujo-civil-basico para generar plataforma_demo.dxf con la demo ficticia de 12 × 8 m de este archivo. Dibujá el contorno cerrado, dos ejes centrales, las dos cotas editables, el título y la nota. Entregá el DXF, el script de generación y un resumen de las comprobaciones.

### Comprobaciones esperadas

- Un contorno rectangular cerrado con cuatro vértices y área de 96 m².
- Dos ejes centrales.
- Dos cotas DIMENSION: 12 y 8 unidades.
- Geometría principal entre X=0 y 12, Y=0 y 8; todas las entidades del modelo con Z=0.
- Las cotas y los rótulos pueden extenderse fuera del contorno.
- Unidades del DXF en metros.

## Entrega

Entregar el DXF editable, el script utilizado si se generó por código y un resumen con unidades, dimensiones, supuestos y validaciones. Si se instaló una biblioteca, registrar su versión para reproducir el resultado.

DWG es opcional: convertir únicamente con una herramienta disponible y verificar el archivo. Cambiar la extensión de DXF a DWG no es una conversión.

## Reutilización

Se permite copiar, adaptar y compartir este archivo. La demo usa medidas ficticias y no contiene claves, datos personales, rutas privadas ni documentación de obras.
