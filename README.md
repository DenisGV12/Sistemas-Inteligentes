# Práctica 1 — Satisfacción de restricciones (crucigrama)

## Sesión 1: representación del problema

El objetivo de esta sesión es traducir el tablero del crucigrama al lenguaje de un
problema de satisfacción de restricciones (CSP):

- **Variables**: cada hueco del crucigrama (horizontal o vertical) donde debe entrar una palabra.
- **Dominio**: las palabras del diccionario que pueden ir en ese hueco.
- **Restricciones**: cada cruce entre un hueco horizontal y uno vertical obliga a que
  ambas palabras compartan la misma letra en la celda común.

Constantes usadas: `LLENA = '*'` (celda negra) y `VACIA = '-'` (celda libre sin letra).

---

## Clase `Variable`

Representa un hueco del crucigrama. Guarda:

| Atributo | Contenido |
|---|---|
| `nombre` | Identificador numérico de la variable (0, 1, 2...) |
| `tipo` | `'h'` si es horizontal, `'v'` si es vertical |
| `celdas` | Lista de pares `(fila, columna)` que ocupa el hueco, en orden |
| `fila`, `col` | Coordenadas de la primera celda, para poder imprimir su posición |
| `dominio` | Lista de palabras candidatas que caben en el hueco |
| `restricciones` | Lista de tuplas `(otraVariable, posEnMi, posEnOtra)` |

El método `__str__` devuelve la variable con el formato que pide el enunciado:

```
Nombre 0 Posición 0 0 Tipo: horizontal Dominio: ['ASILO', 'ESOPO', ...]
```

Cada restricción indica con qué variable se cruza, en qué índice de **mi** palabra
está la letra compartida y en qué índice de la palabra de **la otra**. Así, comprobar
la consistencia entre dos variables asignadas es simplemente:

```python
palabra1[posEnMi] == palabra2[posEnOtra]
```

Esto es lo que se usará en las sesiones siguientes para backtracking, forward
checking y AC3.

---

## Función `recorreTablero(tablero, celdas)`

Recibe un recorrido completo del tablero (una fila entera o una columna entera,
como lista de coordenadas) y lo parte en **tramos** de celdas contiguas libres.

Funcionamiento:

1. Recorre las celdas del recorrido una a una acumulándolas en `aux`.
2. Al encontrar una celda `LLENA`, cierra el tramo: si `aux` no está vacío lo añade
   a `trozosHueco` y lo reinicia.
3. Al terminar el recorrido, si queda un tramo abierto en `aux`, también lo añade.

Devuelve `trozosHueco`, la lista de tramos. Es el equivalente a un `split()` de
cadenas, pero cortando por celdas negras en lugar de por espacios.

La función no distingue entre filas y columnas: eso lo decide quien construye la
lista `celdas` que se le pasa. Por eso sirve igual para los huecos horizontales y
para los verticales.

---

## Función `palabraCabe(tablero, almacen, celdas)`

Calcula el **dominio inicial** de un hueco, es decir, qué palabras del diccionario
pueden colocarse en él.

El diccionario se carga antes con `creaAlmacen(file)`, que lee el fichero de texto y
construye un `almacen`: un diccionario cuya clave es la longitud de la palabra y cuyo
valor es el conjunto de palabras de esa longitud, en mayúsculas. Agrupar por longitud
evita recorrer todo el fichero en cada hueco.

Con eso, `palabraCabe`:

1. Coge del almacén solo las palabras cuya longitud coincide con el número de celdas
   del tramo (`almacen.get(len(celdas), [])` devuelve una lista vacía si no hay
   ninguna palabra de esa longitud, evitando el error de clave inexistente).
2. Para cada palabra comprueba, letra a letra, las celdas que ya tienen una letra
   escrita en el tablero. Si una celda no está `VACIA` y su letra no coincide con la
   de la palabra en esa posición, la palabra se descarta (patrón de bandera:
   `valida = False` y `break`).
3. Devuelve la lista de palabras que han superado la comprobación.

Se usa `sorted(...)` para que el dominio salga siempre en el mismo orden y los
resultados sean reproducibles entre ejecuciones.

---

## Función `creaVariables(tablero, almacen)`

Construye la lista completa de variables del crucigrama a partir del tablero actual.

1. **Horizontales**: por cada fila `f` se genera la lista de todas sus celdas y se pasa
   por `recorreTablero`. Cada tramo obtenido se convierte en una `Variable` de tipo
   `'h'`, con su dominio calculado por `palabraCabe`.
2. **Verticales**: lo mismo por columnas, pero solo se crean variables para tramos de
   **2 o más celdas**. Un tramo vertical de una sola celda no forma palabra y ya queda
   cubierto por la variable horizontal correspondiente.
3. **Restricciones**: se recorren todos los pares de variables de tipo distinto
   (horizontal contra vertical) y se busca si comparten alguna celda. Si la comparten,
   se añade a `v1.restricciones` la tupla `(v2, índice de la celda en v1, índice en v2)`,
   obtenida con `list.index()`.

El nombre de cada variable es `len(variables)` en el momento de crearla, así que la
numeración es correlativa: primero todas las horizontales por filas y después las
verticales por columnas.

---

## Función `imprimeVariables(variables)`

Recorre la lista y muestra cada variable por consola usando su `__str__`. Se llama
desde el botón **Variables** de la interfaz, que construye las variables del tablero
dibujado en ese momento y las imprime.

---

## Prueba realizada

Se ha comprobado sobre el tablero de ejemplo del enunciado, marcando las celdas
negras y las letras fijas con el ratón y pulsando el botón **Variables**. La salida
coincide con la esperada en número de variables, posiciones y dominios.
