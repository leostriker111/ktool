# Cambios

## 0.5.0b1 (beta — rama `beta`)

> En desarrollo. La rama `main` sigue en 0.4.0; esta versión vive en la rama
> `beta` para revisarse en GitHub sin afectar la instalación estable.
> Probar con: `pip install git+https://github.com/leostriker111/ktool.git@beta`

- Máquinas de estado síncronas (circuitos secuenciales). Subpaquete `fsm` con el
  modelo (estados, codificación, transiciones) y las tablas de excitación de
  flip-flops D, T, JK y SR; el tipo de flip-flop se elige.
- Reutiliza el motor de minimización: cada entrada de flip-flop y cada salida es
  una tabla de verdad que pasa por Quine-McCluskey (SOP/POS/XOR).
- Documento nuevo: diagrama de estados en SVG, tabla de transiciones/excitación,
  mapas de Karnaugh y ecuaciones de excitación, decodificador de salida con
  display de 7 segmentos por estado, y circuito combinado.
- CLI: `kmap fsm maquina.json --ff JK` (también D, T, SR) desde un archivo JSON.
- `seg7_strip_svg`: dibuja una palabra/número completo de 7 segmentos en un SVG.
- Ejemplos de muestra en `ejemplos/`: contador decimal 0-9 (decoder BCD con
  don't cares) y letrero giratorio "tool". Cada uno trae `diagrama.svg` y la
  tira de displays en SVG (se ven directo en GitHub).

## 0.4.0

- Reestructura en subpaquetes: core/render/gui.
- Traductor de lenguajes reescrito sobre AST (lexer→parser→ast→codegen):
  parentesis por precedencia y traduccion de expresiones libres (CLI --to, GUI).

## 0.3.0

- Displays insertables en la interfaz (menu Insertar > Display): 7 segmentos y LED.
  Los segmentos encienden en verde segun la fila/estado activo y se conectan por
  nombre con las salidas; la etiqueta de cada segmento o LED se edita con un clic.

## 0.2.2

- GUI: las columnas se cargan con Enter o el boton Aplicar (las flechas ya no
  redibujan en cada clic); los controles se bloquean durante el redibujo. Adios lag.
- GUI: navegacion con flechas y Enter entre celdas; hasta 32 salidas.
- GUI: la barra acepta numeros (b1011, h4D, d77, 0b../0x..) ademas de expresiones.
- Documento: orden correcto de las senales de entrada en el circuito combinado.
- Documento: boton para copiar la tabla de verdad (TSV, pega como tabla en Excel).
- Documento: comparativa de componentes SOP vs POS vs mezcla, con detalle de
  terminos oculto por default.

## 0.2.1

- Circuito completo combinado: ruteo por columnas virtuales (los cables ya no se
  enciman), cada cable en su color y un punto en cada derivacion.
- Interfaz: clic en zona vacia de la tabla deselecciona.
- Documento: las ecuaciones por lenguaje van al final, agrupadas por lenguaje, con un
  boton para copiar el bloque completo de cada lenguaje.
- CLI: `--langs verilog,c,vhdl` para elegir lenguajes y `--no-langs` para omitirlos.
- C usa `bool` (stdbool.h) en lugar de `int`.

## 0.2.0

- Interfaz: seleccion multiple de celdas (arrastrando o con Shift), resaltadas en
  azul; las teclas 1, 0 y x cambian todas las seleccionadas a la vez.
- Interfaz: copiar / pegar / cortar (Ctrl+C/V/X) en formato compatible con Excel.
- Interfaz: renombrar las salidas haciendo clic en su encabezado.
- Interfaz: menu de Ayuda con guia rapida, atajos de teclado y enlace al repositorio.
- XOR/XNOR ahora compite como un camino mas y se elige si es la realizacion mas barata.
- Documento: ecuaciones exportadas a Matematico, Verilog, VHDL, ABEL, Logisim, C,
  Python y LaTeX, con boton para copiar.
- Documento: seccion de circuito completo sugerido con las compuertas AND compartidas
  entre salidas.
- Documento: guia de lectura incluida.

## 0.1.0

Primera versión.

- Tabla de verdad con hasta 6 variables, hasta 10 salidas y columna de notas.
- Minimización SOP y POS con Quine-McCluskey y don't cares.
- Elección automática de la forma más barata por costo de compuertas.
- Detección de XOR/XNOR por paridad.
- Términos reutilizables entre salidas.
- Mapas de Karnaugh y circuitos en SVG dentro de un documento HTML.
- Entrada por expresión, minterminos (decimal/hex/binario) o vector de verdad.
- Interfaz de línea de comandos (`kmap`) e interfaz gráfica (`kmap gui`).
