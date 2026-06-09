# Cambios

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
