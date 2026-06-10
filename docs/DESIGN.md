# Diseño de ktool

Este documento explica cómo está construida la herramienta por dentro: el flujo
general, los módulos, el modelo de datos y los algoritmos. La idea es que quien
quiera leer o modificar el código tenga un mapa antes de meterse a los archivos.

ktool es Python puro y no depende de librerías externas. La interfaz gráfica usa
`tkinter` (incluido con Python) y los mapas y circuitos se dibujan como SVG
escrito a mano, sin librerías de graficación.

---

## 1. Flujo general

Toda entrada termina convertida en una **tabla de verdad**. A partir de ahí cada
salida se resuelve por separado y los resultados se juntan en un documento.

```mermaid
flowchart TD
    subgraph Entrada
        E1["Expresion booleana"]
        E2["Minterminos + don't cares"]
        E3["Vector de verdad"]
        E4["GUI: clics 0/1/x"]
    end

    E1 --> TT["TruthTable<br/>(core.py)"]
    E2 --> TT
    E3 --> TT
    E4 --> TT

    TT --> SOLVE["solve_output por salida<br/>(simplify.py)"]

    SOLVE --> QM["Quine-McCluskey<br/>SOP y POS (qm.py)"]
    SOLVE --> PAR["Deteccion XOR/XNOR<br/>por paridad"]
    QM --> COST["Eleccion por costo<br/>compuertas y literales"]

    COST --> SHARED["Terminos compartidos<br/>entre salidas"]
    PAR --> REP
    COST --> REP
    SHARED --> REP

    REP["Reporte (report.py)"] --> RK["K-map SVG<br/>(render_kmap.py)"]
    REP --> RC["Circuito SVG<br/>(render_circuit.py)"]
    REP --> HTML["Documento HTML"]
```

Los dos puntos de entrada al programa son la **CLI** (`cli.py`) y la **GUI**
(`gui.py`). Ambas construyen una `TruthTable` y llaman al mismo motor, así que
producen resultados idénticos.

---

## 2. Módulos

Cada archivo tiene una responsabilidad y las dependencias van en un solo sentido
(los módulos de presentación dependen del núcleo, nunca al revés).

El paquete está en tres subpaquetes y las dependencias van en un solo sentido:
`gui`/`cli` → `render` → `core`. El núcleo no importa de presentación.

```mermaid
flowchart LR
    cli["cli.py"] --> table["core/table.py"]
    cli --> report["render/report.py"]
    cli --> codegen["render/codegen.py"]
    gui["gui/app.py"] --> table
    gui --> report
    gui --> astm["core/ast.py"]

    report --> simplify["core/simplify.py"]
    report --> kmap["render/kmap.py"]
    report --> circuit["render/circuit.py"]
    report --> codegen

    simplify --> qm["core/qm.py"]
    kmap --> layout["core/kmap_layout.py"]
    kmap --> simplify
    circuit --> simplify
    codegen --> astp["core/parser.py"]
    codegen --> simplify
    table --> astm
    astm --> astp
    astp --> lexer["core/lexer.py"]
```

**Pipeline del traductor (Etapa B):** una sola fuente de verdad.
Texto o `Solution` → AST de tuplas → emisor por precedencia.

```mermaid
flowchart LR
    txt["texto: A'B + C"] --> lex["lexer.tokenize"]
    lex --> par["parser.parse"]
    par --> ast["AST (tuplas)"]
    sol["Solution minimizada"] --> s2a["codegen.solution_to_ast"]
    s2a --> ast
    ast --> emit["codegen.emit(node, lang)"]
    emit --> out["Verilog / VHDL / C / ..."]
```

| Módulo | Responsabilidad |
| --- | --- |
| `core/table.py` | Tabla de verdad y parsing de bases numéricas. |
| `core/kmap_layout.py` | Geometría del K-map (código Gray, particiones). |
| `core/qm.py` | Quine-McCluskey: implicantes primos y cobertura mínima con Petrick. |
| `core/lexer.py` | Tokeniza la expresión booleana (scanner). |
| `core/parser.py` | Parser descendente recursivo → AST de tuplas. |
| `core/ast.py` | Gramática de nodos, `evaluate` sobre los 2^n casos, `build_output`. |
| `core/simplify.py` | Formato de ecuaciones, XOR/XNOR, costo y términos compartidos. |
| `render/kmap.py` | Dibuja el mapa de Karnaugh en SVG con los grupos circulados. |
| `render/circuit.py` | Dibuja el circuito en SVG (rieles de literales y compuertas). |
| `render/codegen.py` | Traductor AST → lenguaje (OPS por lenguaje + `emit` por precedencia). |
| `render/report.py` | Arma el documento HTML uniendo todo. |
| `cli.py` | Línea de comandos y switches (incluye `--to <lang>`). |
| `gui/app.py` | Interfaz gráfica en tkinter. |
| `gui/displays.py` | Displays insertables (7 segmentos / LED). |

---

## 3. Modelo de datos

```mermaid
classDiagram
    class TruthTable {
        +int nvars
        +int rows
        +list variables
        +dict outputs
        +list notes
        +minterms(name)
        +maxterms(name)
        +dontcares(name)
        +bits(index)
        +from_minterms()
        +from_expression()
    }

    class Solution {
        +str form
        +list patterns
        +list variables
        +const
        +equation
        +cost()
    }

    TruthTable "1" --> "varias" Solution : solve_output
```

`outputs` es un diccionario `nombre_de_salida -> lista de 2^n valores`, donde cada
valor es `0`, `1` o `"x"` (don't care). `solve_output` devuelve, por cada salida,
una `Solution` para SOP y otra para POS, más la recomendada y la forma XOR si
aplica.

Un **patrón** es una cadena como `"10-1"`: cada posición corresponde a una
variable, `1` y `0` son literales fijos y `-` es una variable eliminada del
término. De ahí salen tanto las ecuaciones como los grupos del mapa.

---

## 4. Quine-McCluskey

La minimización es el corazón de la herramienta. Es exacta (a diferencia de
agrupar a ojo en el mapa) y maneja don't cares.

```mermaid
flowchart TD
    A["Minterminos + don't cares"] --> B["Combinar pares que difieren<br/>en un solo bit"]
    B --> C{¿Se combino algo?}
    C -- Si --> B
    C -- No --> D["Implicantes primos<br/>(los que no se combinaron)"]
    D --> E["Tabla de cobertura<br/>vs minterminos requeridos"]
    E --> F["Implicantes esenciales"]
    F --> G{¿Faltan<br/>minterminos?}
    G -- No --> H["Cobertura final"]
    G -- Si --> P["Petrick: producto de sumas<br/>-> elegir el conjunto minimo"]
    P --> H
```

Detalles que vale la pena conocer:

- Los **don't cares** entran en la fase de combinación (ayudan a formar grupos
  más grandes) pero **no** se exigen en la cobertura.
- El **POS** se calcula resolviendo el SOP de la función complementada (los ceros)
  y luego invirtiendo la polaridad de cada literal por De Morgan. Se reutiliza el
  mismo motor.
- **Petrick** se aplica solo cuando quedan minterminos sin cubrir después de los
  esenciales. Para 6 variables el tamaño es manejable; aun así se reduce por
  absorción para no explotar.

La elección entre SOP y POS compara el par `(compuertas, literales)` y se queda
con el menor. Por eso `auto` puede recomendar POS cuando sale más barato.

---

## 5. Layout del K-map

Las variables se reparten entre filas y columnas, y dentro de cada eje el orden
es **código Gray** (un solo bit cambia entre celdas vecinas), que es lo que hace
que los grupos queden contiguos.

| Variables | Filas | Columnas | Tamaño |
| --- | --- | --- | --- |
| 2 | A | B | 2 x 2 |
| 3 | A | B C | 2 x 4 |
| 4 | A B | C D | 4 x 4 |
| 5 | A B | C D E | 4 x 8 |
| 6 | A B C | D E F | 8 x 8 |

Para circular un grupo, se calcula qué filas y qué columnas casan con el patrón;
como el mapa es un toroide, un grupo que cruza el borde se dibuja como dos
rectángulos. Cada grupo recibe un color y un pequeño desfase para que se
distingan cuando se traslapan.

---

## 6. CLI contra GUI

```mermaid
sequenceDiagram
    actor U as Usuario
    participant CLI as cli.py / gui.py
    participant Core as TruthTable
    participant S as simplify.solve_output
    participant R as report.build_report

    U->>CLI: expresion / minterminos / clics
    CLI->>Core: construir tabla
    CLI->>R: build_report(tabla, opciones)
    R->>S: resolver cada salida
    S-->>R: SOP, POS, mejor, paridad
    R-->>CLI: HTML
    CLI-->>U: documento / texto en consola
```

La diferencia entre ambas es solo la captura de la entrada y las opciones de
formato. El núcleo (`core`, `qm`, `simplify`) no sabe si lo llamó la terminal o
la ventana.

---

## 7. Empaquetado

- `pyproject.toml` define los comandos `kmap` y `ktool` (entry points).
- `ktool_launcher.py` es el punto de entrada que usa PyInstaller para generar un
  ejecutable único.
- `installer/ktool.iss` (Inno Setup) toma ese ejecutable y arma el instalador que
  lo agrega al `PATH`.
- El flujo de GitHub Actions en `.github/workflows/release.yml` construye el
  ejecutable y el instalador automáticamente cuando se publica una etiqueta `v*`.
