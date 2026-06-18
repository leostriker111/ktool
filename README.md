# ktool

Herramienta de lógica digital por línea de comandos y con interfaz gráfica.
Resuelve los dos mundos de la materia de sistemas digitales:

- **Combinacional:** llena una tabla de verdad (a mano, desde una expresión o
  desde minterminos) y obtén el mapa de Karnaugh, las ecuaciones mínimas en SOP y
  POS, el circuito de compuertas y un documento HTML con todo junto.
- **Secuencial:** describe una máquina de estados y obtén su diagrama de estados,
  la tabla de transiciones/excitación para el flip-flop que elijas (D, T, JK, SR),
  las ecuaciones de cada flip-flop y el decodificador de salida.

Todo en **Python puro**, sin dependencias externas.

> **El comando se llama `ktool`.** `kmap` es un alias histórico (el proyecto nació
> haciendo solo mapas de Karnaugh) y sigue funcionando, pero la forma recomendada
> es `ktool`. Ambos hacen exactamente lo mismo.

---

## Qué hace

**Combinacional**
- Hasta **6 variables** y hasta **32 salidas** en la misma tabla.
- Minimización exacta con **Quine-McCluskey** (maneja *don't cares*).
- Entrega **SOP y POS** con su costo y **elige** la forma más barata por compuertas.
- Considera **XOR/XNOR** y lo elige si es la realización más económica.
- Encuentra **términos reutilizables** entre salidas (compuertas compartidas).
- **Mapa de Karnaugh** con los grupos circulados en colores y el **circuito** en SVG.
- Exporta las ecuaciones a **Verilog, VHDL, ABEL, Logisim, C, Python y LaTeX**.

**Secuencial (máquinas de estado)**
- Modelos **Moore y Mealy**, con la codificación de estados que tú definas.
- **Diagrama de estados** en SVG con las transiciones etiquetadas.
- **Tabla de transiciones y excitación** para flip-flop **D, T, JK o SR** (lo eliges).
- Reutiliza el motor de minimización: cada entrada de flip-flop y cada salida sale
  ya minimizada con su mapa de Karnaugh.
- **Decodificador de salida** con vista de **display de 7 segmentos** por estado.

La explicación de cómo está construido por dentro está en [DESIGN.md](docs/DESIGN.md).

---

## Instalación

### Opción A — Instalador para Windows (recomendada)

Descarga el instalador desde
[Releases](https://github.com/leostriker111/ktool/releases/latest) y ejecútalo;
agrega `ktool` al `PATH`. O en una línea de PowerShell:

```powershell
irm https://raw.githubusercontent.com/leostriker111/ktool/main/get-ktool.ps1 | iex
```

### Opción B — pip (si ya tienes Python)

```powershell
# versión estable (combinacional)
pip install git+https://github.com/leostriker111/ktool.git

# versión beta (incluye máquinas de estado / secuencial)
pip install git+https://github.com/leostriker111/ktool.git@beta
```

Deja disponibles los comandos `ktool` y `kmap`.

### Opción C — Desde el código fuente

```powershell
git clone https://github.com/leostriker111/ktool.git
cd ktool
packaging\install.ps1
```

Sin instalar, desde la carpeta del proyecto, todo funciona con `python -m ktool ...`.

---

## Tutorial rápido

### 1) Combinacional en 30 segundos

Supón que quieres minimizar `Y = A'B + C` y ver el mapa y el circuito:

```powershell
ktool -e "A'B + C" --open
```

Eso abre un documento HTML con la tabla de verdad, el K-map agrupado, las
ecuaciones SOP/POS (marcando la más barata) y el circuito. Otras formas de dar la
misma función:

```powershell
ktool -n 3 -m 1,4,5,6 -d 2,7              # por minterminos (1,4,5,6) y don't cares (2,7)
ktool -n 3 --truth 01x011x1               # por el vector de salida directo
ktool -n 4 -m 0x1,0b11,5 --text           # mezcla decimal/hex/bin, ecuaciones en consola
```

Si solo quieres las compuertas, sin K-map ni tabla: agrega `--gates-only`.
Para varias salidas a la vez conviene la interfaz gráfica: `ktool gui`.

### 2) Secuencial: una máquina de estados

Describe la máquina en un archivo JSON y pásala con el subcomando `fsm`:

```powershell
ktool fsm maquina.json --ff JK
```

`--ff` elige el flip-flop: `D`, `T`, `JK` o `SR`. El documento trae el diagrama de
estados, la tabla de transición/excitación, los mapas de Karnaugh de cada entrada
de flip-flop, las ecuaciones y el decodificador de salida.

Formato del JSON (ejemplo de un contador 0-9 a 7 segmentos):

```json
{
  "name": "Contador decimal 0-9",
  "kind": "moore",
  "inputs": [],
  "state_bits": ["Q3", "Q2", "Q1", "Q0"],
  "outputs": ["a", "b", "c", "d", "e", "f", "g"],
  "states": [
    { "name": "D0", "code": "0000", "label": "0", "out": "1111110" },
    { "name": "D1", "code": "0001", "label": "1", "out": "0110000" }
  ],
  "transitions": [
    { "from": "D0", "in": "", "to": "D1" },
    { "from": "D1", "in": "", "to": "D0" }
  ]
}
```

| Campo | Qué es |
| --- | --- |
| `kind` | `moore` (la salida depende del estado) o `mealy` (depende de estado y entrada). |
| `inputs` | Lista de entradas; `[]` = contador libre (solo reloj). |
| `state_bits` | Las variables de estado / flip-flops (MSB primero). |
| `outputs` | Nombres de las salidas (p. ej. los segmentos `a`…`g`). |
| `states` | `code` = codificación binaria; `out` = salida en ese estado (Moore); `label` = etiqueta del diagrama. |
| `transitions` | `in` = bits de las entradas que disparan la transición (`""` si no hay entradas). |

Hay ejemplos completos y listos para correr en la carpeta
[`ejemplos/`](ejemplos): un **contador decimal 0-9** (decoder BCD) y un **letrero
giratorio**. Cada uno trae su `diagrama.svg` y la tira de displays en SVG.

---

## Referencia de la terminal

```powershell
ktool [-e EXPR | -m MINTERMS | --truth VECTOR] [opciones]   # combinacional
ktool fsm ARCHIVO.json [--ff D|T|JK|SR] [opciones]          # secuencial
ktool gui                                                    # interfaz gráfica
ktool -h                                                     # ayuda completa
```

### Opciones (combinacional)

| Switch | Para qué sirve |
| --- | --- |
| `-n, --vars N` | Número de variables (2 a 6). |
| `-e, --expr "..."` | Expresión booleana; arma la tabla evaluando todos los casos. |
| `-m, --minterms ...` | Lista de minterminos en decimal, `0x` hex o `0b` bin. |
| `-d, --dontcares ...` | Lista de *don't cares* (misma sintaxis). |
| `--truth 01x10...` | Vector de salida directo (largo `2^n`, admite `x`). |
| `--form sop\|pos\|auto\|both` | Forma a mostrar. `auto` elige la más barata. |
| `--gates-only` | Solo compuertas (apaga K-map y tabla). |
| `--text` | Solo imprime las ecuaciones en la terminal. |
| `--out archivo.html` / `--open` | Guardar el HTML / abrirlo en el navegador. |

### Opciones (`fsm`)

| Switch | Para qué sirve |
| --- | --- |
| `--ff D\|T\|JK\|SR` | Tipo de flip-flop para la tabla de excitación (default `JK`). |
| `--out archivo.html` | Ruta del HTML. |
| `--no-open` | No abrir el navegador. |
| `--no-circuit` | No dibujar circuitos. |
| `--langs verilog,vhdl` / `--no-langs` | Elegir o quitar el bloque de lenguajes. |

### Sintaxis de expresiones

| Operación | Cómo se escribe |
| --- | --- |
| AND | `ab`, `a*b`, `a.b`, `a&b` |
| OR | `a+b`, `a\|b` |
| NOT | `a'`, `!a`, `~a` |
| XOR | `a^b` |
| XNOR | `(a^b)'` |

Las variables son letras `A` a `F`. Precedencia: NOT, luego AND, luego XOR, luego OR.

---

## Interfaz gráfica

```powershell
ktool gui
```

Tabla al estilo de un solucionador clásico. Arriba eliges el número de variables y
de salidas, la columna de notas y la forma (SOP, POS, auto o ambas). La barra de
expresión llena una columna evaluando lo que escribas; *Generar documento* arma el
HTML. Para llenar rápido: selecciona celdas arrastrando (o Shift+clic), y con la
selección las teclas `1`/`0`/`x` las cambian todas; doble clic cicla una celda
`0 → 1 → x`; Ctrl+C/V/X copia-pega estilo Excel; clic en el encabezado renombra la
salida. El menú *Ayuda* tiene la guía y los atajos.

---

## Alcance

Proyecto de práctica, no una herramienta de diseño profesional. Las cuentas son
exactas (tabla de verdad + Quine-McCluskey), pero conviene confirmar la salida si
la vas a usar para algo serio.

Limitaciones conocidas:

- La detección de XOR/XNOR aplica cuando la función completa es la paridad de un
  subconjunto de variables; no factoriza XOR parciales dentro de un SOP grande.
- En secuencial, dibuja la lógica combinacional de cada entrada de flip-flop y el
  circuito combinado, pero todavía no un esquemático único a nivel flip-flop con el
  reloj; tampoco minimiza estados (asume que ya diste los estados mínimos).
- No incluye álgebra de Boole simbólica sobre expresiones arbitrarias.

---

## Contribuir

Sugerencias y reportes son bienvenidos: abre un *issue* o manda un *pull request*.
La rama `main` es la versión estable; el desarrollo nuevo va en `beta`. Mira
[CONTRIBUTING.md](CONTRIBUTING.md).

---

## Licencia

[MIT](LICENSE). Hecho por Leostriker.
