# Verificación y entrega

Estas fases validan recorridos completos desde la interfaz de Synapsis. Usá un ejercicio propio equivalente al de la guía y anotá resultado esperado, resultado obtenido, plataforma y commit en la evidencia.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| V01 ✓ | Verificar una sesión docente por vez. | Registrar en COBERTURA entrada mínima, método elegido, cálculo reproducible a mano, caso de fallo y verificación. Cubrir las 22 sesiones y los Programas 1–9. |
| V02 ✓ | Verificar una semana de Cálculo por vez. | Contrastar con el índice de las 15 semanas de I y las 16 de II. En especial, el ejercicio de área del segundo corte termina al plantear la integral. |
| V03 ✓ | Verificar edición y vuelta desde resultados. | Reabrir un caso del historial, modificar un valor y comprobar que fórmula, pasos, tabla y gráfico se actualizan juntos en modo claro y oscuro. |
| V04 ✓ | Verificar portada en un cambio que use archivos compartidos. | Comparar capturas con la base aprobada a iguales dimensiones, preferencia de movimiento e instante. Comprobar continuidad visual al desplazarse y al entrar y salir del modo serio. |
| V05 ✓ | Verificar una gráfica por sesión. | La fila elegida, su fórmula y sus marcas coinciden. Pausa y teclado funcionan; un estado vacío o un método detenido conserva la explicación. |
| V06 ✓ | Medir una interacción lenta. | Registrar equipo, escenario y tiempo antes y después. Comprobar cálculo, carga diferida de pasos y número de repintados con el mismo ejercicio. |
| V07 · parcial | Probar el arranque de escritorio en Windows. | Abrir desde el archivo Python con dependencias instaladas y desde Inicio tras instalar el EXE en un equipo limpio. Resolver y cerrar. Comprobar ventana propia, motor Python local y archivos del teclado accesibles tras la instalación inicial. |
| V08 · parcial | Verificar la distribución ZIP desde main. | Extraer el proyecto completo en otra carpeta, comprobar la entrada Python, el index.html para Go Live, dependencias, licencias y activos locales y resolver un caso. Registrar el SHA fuente del ZIP. |

Para verificar Pages, el instalador Windows y el APK firmado, seguir la [guía de plataformas](09-plataformas.md). Para la paridad matemática y gráfica, aplicar los [criterios de calidad](10-calidad.md).

## Evidencia de la verificación

La base de comparación fue `af8723d61903f5135c65432087f28ae89a10da86`. Los recorridos y las mediciones se ejecutaron sobre el árbol de `e68ccc91c5eeced82384a9687c0507ea7c07e30b` en Debian 13 x86-64, Intel Xeon Platinum 8573C, Python 3.12 y Qt WebEngine 6.10.2 con renderizado sin GPU. Se probaron ventanas de 390×900 y 1366×900.

| Fase | Resultado observado |
| --- | --- |
| V01 | 22 ejercicios propios y 22 casos límite atravesaron Formulario, Resolver y Procedimiento. Los programas 1 a 9 están vinculados a sus técnicas y a las comprobaciones independientes. [Casos y datos mínimos](../COBERTURA.md#v01--sesiones-0122-y-programas-19). |
| V02 | Se contrastó el índice de 15 semanas de Cálculo I y 16 de Cálculo II y se ejecutó una técnica representativa por semana. En el caso del segundo corte se mostró $\int_0^1(x-x^2)\,dx$ y se comprobaron los cruces 0 y 1. El panel se detuvo en el planteamiento. [Ejercicios y fuentes docentes](../COBERTURA.md#v02--semanas-de-cálculo-i-y-ii). |
| V03 | En modo claro y oscuro se recuperó $x^2-2$ del historial y, desde Editar datos, se cambió a $x^2-3$. La cabecera, la fila de la tabla, la traza y las muestras se verificaron contra el cálculo nuevo. El flujo también detectó y corrigió el ancho del procedimiento a 390 px. |
| V04 | Coincidieron píxel por píxel las capturas de portada y del menú serio a ambos anchos con la animación pausada. Se desplazó la portada 350 píxeles, se entró al modo serio y se comprobó que al volver se recuperaran la posición y la geometría visible, con tolerancia de 1 píxel. |
| V05 | La fila 30 de Bisección seleccionó el marcador y la fórmula de esa iteración. Las flechas avanzaron la gráfica y el procedimiento. Se probó reproducción y pausa. En Newton detenido desde cero, la interfaz conservó el último punto y el residuo 2. El control de Riemann actualizó en conjunto los rectángulos, el número de muestras y la suma. |
| V06 | Se eliminó el dibujo del lienzo mientras está separado de la vista. En el mismo ejercicio, la primera apertura de la gráfica pasó de 3 dibujos a 1. Elegir otra fila con la gráfica oculta pasó de 1 dibujo a 0. La primera apertura de Procedimiento mantuvo 18 de 43 pasos en pantalla. |
| V07 | `abrir.py` abrió la ventana Qt con el motor local en Windows Server 2025, compilación 26100. El teclado local ingresó $x^3$, se obtuvo $3x^2$ con KaTeX y pasos, y al cerrar se liberó el puerto. La prueba bloqueó peticiones a servidores externos después de instalar las dependencias. Queda la verificación desde Inicio con el EXE e instalador de P11–P12. [Ejecución de Windows](https://github.com/Rolando8-03/Synapsis/actions/runs/45312526011). |
| V08 | Se archivó la base de `main` en ZIP y se extrajo en una carpeta nueva. Se instaló `requirements.txt` en un entorno virtual limpio. Se comprobaron las licencias de Three, KaTeX, MathLive y tipografías, los activos locales y el cálculo $d(x^3)/dx=3x^2$ desde la ventana. El servidor estático entregó `dist/index.html` con HTTP 200. El `index.html` raíz y el catálogo con servidor estático devolvieron HTTP 404. La verificación de Go Live depende de P09. |

### Medición de V06

Se ejecutó cinco veces Bisección para $x^2-2$ en [1,2], con tolerancia $10^{-12}$, en Qt a 1366×900. La tabla usa la mediana de las cuatro repeticiones después del primer cálculo. Se usó el mismo motor Python para ambas mediciones.

| Señal | Base | Con la corrección |
| --- | ---: | ---: |
| Respuesta HTTP de cálculo y lectura del resultado | 21,05 ms | 20,20 ms |
| Apertura de la pestaña Gráfica | 5,55 ms | 3,75 ms |
| Dibujos al abrir Gráfica por primera vez | 3 | 1 |
| Dibujos al seleccionar una fila con la gráfica oculta | 1 | 0 |
| Pasos en el primer lote / total | 18 / 43 | 18 / 43 |

### Repetir los recorridos

```sh
python -m unittest discover -s pruebas -v
node --test pruebas/test_expression_input.mjs
python -m pruebas.entrega.interfaz --ancho 390
python -m pruebas.entrega.interfaz --ancho 1366
python -m pruebas.entrega.arranque
git worktree add --detach ../synapsis-base-entrega af8723d61903f5135c65432087f28ae89a10da86
python -m pruebas.entrega.portada --base ../synapsis-base-entrega/dist --ancho 390
python -m pruebas.entrega.portada --base ../synapsis-base-entrega/dist --ancho 1366
python -m pruebas.entrega.interfaz --medir --dist ../synapsis-base-entrega/dist
python -m pruebas.entrega.interfaz --medir
```

Para repetir V08, identificá el commit con `git rev-parse origin/main`, usalo en `git archive --format=zip --prefix=Synapsis/ --output=Synapsis.zip <SHA>`, extraé el ZIP y probá la entrada Python desde esa copia. El ZIP local de la base archivada dio SHA-256 `c917de53b9c7c6a2b16b89ad62e7e135a3abc9e04a823c21b173cccb2f94febf`.
