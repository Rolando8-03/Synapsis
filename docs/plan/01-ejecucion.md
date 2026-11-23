# Cómo ejecutar una fase

> Implementá únicamente la fase [ID] sobre la última versión de main. Buscá primero la operación existente y sus pruebas. Entregá el criterio de cierre de esa fila por su entrada habitual. Verificá lo afectado, integrá en main y devolvé ID, prueba y enlace al commit.

Cuando una fila indique «por sesión» o enumere variantes sucesivas, usá un ID con sufijo por variante (por ejemplo, C08-cadena e I06-seno-coseno). Cada sufijo tiene su propio commit en main. Si una fase de algoritmo aún no tiene datos para completar una vista, integrá la función probada y conectá la vista en la fase dependiente.

1. Actualizá desde `main`. Revisá si el ID ya se integró y si el ejemplo de cierre ya funciona. Si funciona, registrá la evidencia junto al ID en esta guía o en la guía temática y evitá reescribir la operación.
2. Acotá el cambio a una decisión, un método o una vista. Si una fila necesita más de una sesión, dividila en subfases identificadas antes de programar y cerrá solo la primera. El número de créditos depende de la sesión. Usá los ejemplos pequeños de cada fila para limitar el trabajo.
3. Probá un caso representativo y un caso límite por la ruta habitual. Para cambios matemáticos calculá una referencia independiente o comprobá la identidad en los datos originales. Agregá una prueba de regresión cuando las existentes no detecten el fallo.
4. Corré `python -m unittest discover -s pruebas -v` desde la raíz. Para UI comprobá la interacción afectada. Integrá el commit en **main**, directamente o mediante un PR pequeño fusionado. Si la rama avanzó, conservá esos cambios y repetí la verificación. Un PR abierto queda pendiente.
5. Registrá el ID en el mensaje de commit y comprobá su presencia en `main`. Informá qué caso pasó y cualquier limitación comprobada. Las fuentes docentes se consultan por enlace. Publicá ejemplos propios y atribuciones, sin incorporar copias de los libros.

## Programación estructurada y orientada a objetos en este proyecto

| Responsabilidad | Punto de extensión |
| --- | --- |
| Entrada | `backend.catalog`, `backend.calculate`, `application/catalog.py` y `application/service.py` en `motor_matematico/`. Verificá dimensiones, dominio y opciones según la salida elegida. Conservá identificadores, formato serializado y reapertura del historial. |
| Algoritmos en Python | Escribí funciones pequeñas con entradas, salida y condiciones de parada explícitas. Separá validación, cálculo y comprobación. Reutilizá `reduction.py`, `factorization.py`, `spaces.py`, `worked.py` y las funciones que ya invoca el despachador de Synapsis. Conservá las fracciones durante las cuentas exactas. |
| Objetos del dominio | Usá `Problem`, `Step` y `CalculationResult` de `motor_matematico/domain/models.py` donde la ruta ya use ese contrato. `OperationSpec` describe los campos. `Context` recoge pasos y progreso. Para Kepler, un objeto de parámetros orbitales puede garantizar sus invariantes mientras funciones puras calculan posiciones. Introducí una clase solo si reúne datos y comportamiento compartidos. |
| Desarrollo docente | Emití desde la ejecución la regla, sus hipótesis, los operandos, sustitución, simplificación y verificación. `procedimientos.py` adapta trazas existentes. Una prueba con números verifica un caso. Una demostración general requiere variables y las hipótesis correspondientes. |
| Presentación | `dist/workspace.js`, `workspace-results.js`, `matrix-input.js`, `math-format.js`, `plot.js` y `orbit.js` dentro de `dist/` consumen los resultados. Toda matemática de resolución reside en Python. Las gráficas usan las muestras de la misma ejecución. |

**Referencia docente.** Contrastá cada familia con su sesión en `temario.py` y su guía en [COBERTURA](../../COBERTURA.md). El crédito académico por el algoritmo exige explicar también el caso en que el método se detiene.
