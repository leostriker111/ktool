# ktool

Simplificador de lógica digital por línea de comandos y con interfaz gráfica.
Llena una tabla de verdad (a mano, desde una expresión o desde una lista de
minterminos) y obtén el mapa de Karnaugh, las ecuaciones mínimas en SOP y POS,
el diagrama de compuertas y un documento HTML con todo junto.

Pensado para la materia de sistemas digitales: trabaja con varias salidas a la
vez, elige la forma más barata por número de compuertas, detecta XOR/XNOR y
señala los términos que se pueden reutilizar entre salidas para ahorrar
componentes.

> **El comando se llama `ktool`.** `kmap` es un alias histórico (el proyecto nació
> haciendo solo mapas de Karnaugh) y sigue funcionando igual; ambos hacen lo mismo.

---

## Qué hace

- Hasta **6 variables** y hasta **10 salidas** en la misma tabla.
- Columna de **notas** opcional para nombrar cada estado (por ejemplo `0000` → `L`).
- Minimización exacta con **Quine-McCluskey** (maneja *don't cares*).
- Entrega **SOP y POS** al mismo tiempo, con el costo de cada forma.
- **Elige automáticamente** la forma más conveniente por compuertas y literales.
- Considera **XOR/XNOR** como un camino más y lo elige si es la realización más barata.
- Encuentra **términos reutilizables** entre salidas (compuertas compartidas).
- Genera un **mapa de Karnaugh** con los grupos circulados en colores.
- Dibuja el **circuito** por salida y un **circuito completo combinado** con las
  compuertas compartidas entre todas las salidas.
- Exporta las ecuaciones a **Verilog, VHDL, ABEL, Logisim, C, Python y LaTeX**, con
  botón para copiar al portapapeles.
- Construye la tabla **a partir de una expresión booleana** evaluando los 2^n casos.
- Acepta minterminos en **decimal, hexadecimal (`0x`) o binario (`0b`)**.
- Todo en **Python puro**, sin dependencias externas.

La explicación de cómo está construido por dentro está en [DESIGN.md](docs/DESIGN.md).

---

## Instalación

### Opción A — Instalador para Windows (recomendada)

Descarga el instalador más reciente desde la página de
[Releases](https://github.com/leostriker111/ktool/releases/latest) y ejecútalo.
El instalador agrega `ktool` al `PATH`, así que después puedes llamarlo desde
cualquier terminal.

O en una línea de PowerShell (descarga y lanza el instalador más reciente):

```powershell
irm https://raw.githubusercontent.com/leostriker111/ktool/main/get-ktool.ps1 | iex
```

### Opción B — pip (si ya tienes Python)

```powershell
pip install git+https://github.com/leostriker111/ktool.git
```

Esto deja disponibles los comandos `ktool` y `kmap` (alias).

### Opción C — Desde el código fuente

```powershell
git clone https://github.com/leostriker111/ktool.git
cd ktool
packaging\install.ps1
```

`packaging\install.ps1` copia la herramienta a tu carpeta de usuario y la agrega al `PATH`
(requiere tener Python instalado).

---

## Uso por terminal

```powershell
ktool -e "A'B + C" --open                 # construir tabla desde una expresion
ktool -n 3 -m 1,4,5,6 -d 2,7             # minterminos y don't cares
ktool -n 4 -m 0x1,0b11,5 --text         # mezcla de bases, ecuaciones en consola
ktool -n 3 --truth 01x011x1 --form both # vector de salida directo
ktool ... --gates-only                   # solo compuertas (sin K-map ni tabla)
ktool gui                                 # abrir la interfaz grafica
ktool -h                                  # ayuda completa
```

Sin instalar, desde la carpeta del proyecto, usa `python -m ktool ...`.

### Opciones

| Switch | Para qué sirve |
| --- | --- |
| `-n, --vars N` | Número de variables (2 a 6). |
| `-e, --expr "..."` | Expresión booleana; arma la tabla evaluando todos los casos. |
| `-m, --minterms ...` | Lista de minterminos en decimal, `0x` hex o `0b` bin. |
| `-d, --dontcares ...` | Lista de *don't cares* (misma sintaxis). |
| `--truth 01x10...` | Vector de salida directo (largo `2^n`, admite `x`). |
| `--name Y` | Nombre de la salida. |
| `--form sop\|pos\|auto\|both` | Forma a mostrar. `auto` elige la más barata. |
| `--no-kmap` | No incluir mapas de Karnaugh. |
| `--no-circuit` | No incluir circuitos. |
| `--no-table` | No incluir la tabla de verdad. |
| `--gates-only` | Solo compuertas (apaga K-map y tabla). |
| `--text` | Solo imprime las ecuaciones en la terminal. |
| `--out archivo.html` | Ruta del documento HTML a generar. |
| `--open` | Abre el documento en el navegador. |
| `--title "..."` | Título del documento. |

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
de salidas, activas la columna de notas y la forma (SOP, POS, auto o ambas). La
barra de expresión llena una columna evaluando lo que escribas. El botón
*Ecuaciones* muestra el resultado en el panel inferior y *Generar documento* arma el
HTML.

Para llenar la tabla rápido:

- **Selecciona** varias celdas arrastrando con el ratón (o Shift+clic para agregar);
  quedan resaltadas en azul.
- Con la selección hecha, las teclas **`1`**, **`0`** y **`x`** cambian todas a la vez.
- **Doble clic** cicla una sola celda `0 -> 1 -> x`.
- **Ctrl+C / Ctrl+V / Ctrl+X** copian, pegan y cortan en formato compatible con Excel.
- **Clic en el encabezado** de una salida para renombrarla.

El menú *Ayuda* tiene la guía rápida, la lista de atajos y el enlace al repositorio.

---

## Salida

El documento HTML reúne, por cada salida: las ecuaciones SOP y POS con su costo,
la forma recomendada, el mapa de Karnaugh con los grupos en colores, el circuito
y la tabla de verdad. Cuando hay varias salidas, agrega una sección con los
términos que aparecen en más de una (las compuertas que se pueden compartir).

---

## Alcance

Esto es un proyecto de práctica, no una herramienta de diseño profesional.
Las cuentas se hacen con tabla de verdad más Quine-McCluskey, que es exacto,
pero conviene confirmar la salida si la vas a usar para algo serio.

Limitaciones conocidas:

- La detección de XOR/XNOR aplica cuando la función completa es la paridad de un
  subconjunto de variables; no factoriza XOR parciales dentro de un SOP grande.
- El circuito asume disponibles los literales complementados (rieles `A'`) y no
  dibuja un esquemático único con las compuertas compartidas; esas se listan
  aparte.
- No incluye álgebra de Boole simbólica sobre expresiones arbitrarias.

---

## Contribuir

Las sugerencias y reportes son bienvenidos. Abre un *issue* para proponer algo o
manda un *pull request*. La rama `main` está protegida, así que los cambios
entran por PR. Mira [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Licencia

[MIT](LICENSE). Hecho por Leostriker.
