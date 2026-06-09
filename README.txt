ktool
=====

Simplificador de logica digital por linea de comandos y con interfaz grafica.
Llena una tabla de verdad (a mano, desde una expresion o desde una lista de
minterminos) y obten el mapa de Karnaugh, las ecuaciones minimas en SOP y POS,
el diagrama de compuertas y un documento HTML con todo junto.

Pensado para la materia de sistemas digitales: trabaja con varias salidas a la
vez, elige la forma mas barata por numero de compuertas, detecta XOR/XNOR y
senala los terminos que se pueden reutilizar entre salidas para ahorrar
componentes.


QUE HACE
--------

- Hasta 6 variables y hasta 10 salidas en la misma tabla.
- Columna de notas opcional para nombrar cada estado (por ejemplo 0000 -> L).
- Minimizacion exacta con Quine-McCluskey (maneja don't cares).
- Entrega SOP y POS al mismo tiempo, con el costo de cada forma.
- Elige automaticamente la forma mas conveniente por compuertas y literales.
- Considera XOR/XNOR como un camino mas y lo elige si es la realizacion mas barata.
- Encuentra terminos reutilizables entre salidas (compuertas compartidas).
- Genera un mapa de Karnaugh con los grupos circulados en colores.
- Dibuja el circuito por salida y un circuito completo combinado con las compuertas
  compartidas entre todas las salidas.
- Exporta las ecuaciones a Verilog, VHDL, ABEL, Logisim, C, Python y LaTeX, con boton
  para copiar al portapapeles.
- Construye la tabla a partir de una expresion booleana evaluando los 2^n casos.
- Acepta minterminos en decimal, hexadecimal (0x) o binario (0b).
- Todo en Python puro, sin dependencias externas.

La explicacion de como esta construido por dentro esta en DESIGN.md.


INSTALACION
-----------

Opcion A - Instalador para Windows (recomendada)

  Descarga el instalador mas reciente desde la pagina de Releases y ejecutalo:
  https://github.com/leostriker111/ktool/releases/latest
  El instalador agrega kmap al PATH, asi que despues puedes llamarlo desde
  cualquier terminal.

  O en una linea de PowerShell:
  irm https://raw.githubusercontent.com/leostriker111/ktool/main/get-ktool.ps1 | iex

Opcion B - pip (si ya tienes Python)

  pip install git+https://github.com/leostriker111/ktool.git
  Esto deja disponibles los comandos kmap y ktool.

Opcion C - Desde el codigo fuente

  git clone https://github.com/leostriker111/ktool.git
  cd ktool
  .\install.ps1
  install.ps1 copia la herramienta a tu carpeta de usuario y la agrega al PATH
  (requiere tener Python instalado).


USO POR TERMINAL
----------------

  kmap -e "A'B + C" --open                 construir tabla desde una expresion
  kmap -n 3 -m 1,4,5,6 -d 2,7              minterminos y don't cares
  kmap -n 4 -m 0x1,0b11,5 --text          mezcla de bases, ecuaciones en consola
  kmap -n 3 --truth 01x011x1 --form both  vector de salida directo
  kmap ... --gates-only                    solo compuertas (sin K-map ni tabla)
  kmap gui                                  abrir la interfaz grafica
  kmap -h                                   ayuda completa

Sin instalar, desde la carpeta del proyecto, usa: python -m ktool ...

Opciones:

  -n, --vars N            Numero de variables (2 a 6).
  -e, --expr "..."        Expresion booleana; arma la tabla evaluando todo.
  -m, --minterms ...      Minterminos en decimal, 0x hex o 0b bin.
  -d, --dontcares ...     Don't cares (misma sintaxis).
  --truth 01x10...        Vector de salida directo (largo 2^n, admite x).
  --name Y                Nombre de la salida.
  --form sop|pos|auto|both  Forma a mostrar. auto elige la mas barata.
  --no-kmap               No incluir mapas de Karnaugh.
  --no-circuit            No incluir circuitos.
  --no-table              No incluir la tabla de verdad.
  --gates-only            Solo compuertas (apaga K-map y tabla).
  --text                  Solo imprime las ecuaciones en la terminal.
  --out archivo.html      Ruta del documento HTML a generar.
  --open                  Abre el documento en el navegador.
  --title "..."           Titulo del documento.

Sintaxis de expresiones:

  AND    ab   a*b   a.b   a&b
  OR     a+b  a|b
  NOT    a'   !a    ~a
  XOR    a^b
  XNOR   (a^b)'

Las variables son letras A a F. Precedencia: NOT, luego AND, luego XOR, luego OR.


INTERFAZ GRAFICA
----------------

  kmap gui

Tabla al estilo de un solucionador clasico. Arriba eliges el numero de variables y
de salidas, activas la columna de notas y la forma (SOP, POS, auto o ambas). La
barra de expresion llena una columna evaluando lo que escribas. El boton Ecuaciones
muestra el resultado en el panel inferior y Generar documento arma el HTML.

Para llenar la tabla rapido:

- Selecciona varias celdas arrastrando con el raton (o Shift+clic para agregar);
  quedan resaltadas en azul.
- Con la seleccion hecha, las teclas 1, 0 y x cambian todas a la vez.
- Doble clic cicla una sola celda 0 -> 1 -> x.
- Ctrl+C / Ctrl+V / Ctrl+X copian, pegan y cortan en formato compatible con Excel.
- Clic en el encabezado de una salida para renombrarla.

El menu Ayuda tiene la guia rapida, la lista de atajos y el enlace al repositorio.


SALIDA
------

El documento HTML reune, por cada salida: las ecuaciones SOP y POS con su costo,
la forma recomendada, el mapa de Karnaugh con los grupos en colores, el circuito
y la tabla de verdad. Cuando hay varias salidas, agrega una seccion con los
terminos que aparecen en mas de una (las compuertas que se pueden compartir).


ALCANCE
-------

Esto es un proyecto de practica, no una herramienta de diseno profesional.
Las cuentas se hacen con tabla de verdad mas Quine-McCluskey, que es exacto,
pero conviene confirmar la salida si la vas a usar para algo serio.

Limitaciones conocidas:

- La deteccion de XOR/XNOR aplica cuando la funcion completa es la paridad de un
  subconjunto de variables; no factoriza XOR parciales dentro de un SOP grande.
- El circuito asume disponibles los literales complementados (rieles A') y no
  dibuja un esquematico unico con las compuertas compartidas; esas se listan
  aparte.
- No incluye algebra de Boole simbolica sobre expresiones arbitrarias.


CONTRIBUIR
----------

Las sugerencias y reportes son bienvenidos. Abre un issue para proponer algo o
manda un pull request. La rama main esta protegida, asi que los cambios entran
por PR. Mira CONTRIBUTING.md.


LICENCIA
--------

MIT (ver archivo LICENSE). Hecho por Leostriker.
