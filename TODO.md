# Pendientes

## Release 3 — Maquinas de estado (en diseño)

Objetivo: que ktool reciba un diagrama / tabla de estados y entregue los pasos
completos de diseño de una maquina de estados sincrona, reutilizando el motor de
minimizacion que ya existe.

### Flujo previsto

1. **Entrada de la maquina**
   - Estados, entradas y, por transicion, el estado siguiente y la salida.
   - Soportar Moore (salida depende del estado) y Mealy (salida depende de estado
     y entrada).
   - Formatos a considerar: un DSL de texto sencillo, JSON, o una pestaña en la GUI
     con tabla de transiciones. Probablemente arrancar por texto/JSON para la CLI.

2. **Asignacion de estados (encoding)**
   - Binario, Gray o one-hot. Asignar bits -> variables de estado Q1..Qm.
   - Dejar el encoding elegible; por defecto binario.

3. **Tabla de transiciones expandida**
   - Para cada (bits de estado actual, bits de entrada) -> bits de estado siguiente
     y salidas. Esto ya es una tabla de verdad sobre (Q..., entradas).

4. **Tipo de flip-flop y tabla de excitacion**
   - Elegir D, JK o T.
   - Derivar la excitacion: D = bit siguiente; para JK/T usar la transicion
     actual->siguiente con la tabla de excitacion del flip-flop.

5. **Ecuaciones y circuito**
   - Cada entrada de flip-flop (D, J, K, T) y cada salida es una funcion sobre
     (Q..., entradas): se pasa por `solve_output` para minimizar (SOP/POS/XOR).
   - Aprovechar `build_shared_circuit` para compartir compuertas entre las
     ecuaciones de excitacion y de salida.
   - Render: diagrama de estados, tabla de transiciones/excitacion, ecuaciones y
     el circuito con los flip-flops.

### Como encaja con lo que ya hay

- `core` / `qm` / `simplify` se reutilizan tal cual: una maquina de estados son
  varias tablas de verdad (una por entrada de flip-flop y por salida).
- Modulo nuevo `ktool/fsm.py` para el modelo (estados, transiciones, encoding,
  excitacion) y `render` para el diagrama de estados (SVG) y el circuito con FFs.
- CLI: subcomando `kmap fsm ...` que lea el archivo de la maquina.
- GUI: una pestaña aparte para capturar transiciones.

### Preguntas abiertas / decisiones a tomar

- Formato de entrada de la maquina (DSL propio vs JSON vs tabla en GUI).
- Minimizacion de estados (tabla de implicaciones) antes de asignar: ¿se incluye o
  se asume que el usuario ya tiene los estados minimos?
- Dibujo del diagrama de estados: layout automatico (es lo mas complicado) o
  posiciones simples en circulo.
- Manejo de don't cares en transiciones no especificadas.
