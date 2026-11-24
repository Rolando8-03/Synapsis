# Calidad matemática y gráficas manipulables

Photomath es la referencia de profundidad de explicación y GeoGebra la referencia de exploración gráfica. Evaluá Synapsis con casos reproducibles de los cursos y de los cuatro libros. Una función queda cubierta cuando entrega el resultado solicitado, sus pasos y la validación correspondiente por la entrada habitual. El alcance es la solución matemática y la visualización interactiva con identidad propia.

| Fase | Una tarea | Prueba para integrar |
| --- | --- | --- |
| Q01 | Elegir un ejercicio de referencia para una operación por sesión. | Registrar objetivo mínimo, dominio, referencia independiente y desarrollo esperado. Incluir un caso de frontera. Vincularlo con A, C, I o L y con V01 o V02. |
| Q02 | Evaluar la explicación completa de ese ejercicio. | Se puede reconstruir cada paso a mano. Ejemplo: en la regla de la cadena se ven función interior, derivada exterior, sustitución, producto y verificación en el dominio. Una cuenta exacta conserva sus fracciones. |
| Q03 | Verificar el alcance del resultado solicitado. | Un planteamiento de área termina en la integral. Si el cálculo falla se indica la condición y el último paso válido. La verificación de un método aproximado incluye criterio de parada y residuo. |
| Q04 | Añadir manipulación directa a una escena por sesión. | Empezar con un punto arrastrable en dos rectas. Cambian ecuaciones, cruce y clasificación. Pan, zoom y restablecer vista conservan los datos. Usar la misma acción por teclado. |
| Q05 | Vincular un parámetro de cálculo a la geometría. | En sesiones distintas probar la tangente al variar x, la región entre curvas y la sección de una arandela. Cambian a la vez las etiquetas, fórmulas y tabla. Respetar huecos, discontinuidades y escalas de ejes. |
| Q06 | Animar una construcción matemática verificable. | Usar U11–U12 para recorrer una órbita, un algoritmo o una transformación. Controles de tiempo, velocidad y pausa reproducen el mismo instante. La escena 3D ofrece giro y zoom; una vista pausada permite leer medidas y pasos. |
| Q07 | Medir respuesta con una escena de referencia por dispositivo. | Registrar hardware, navegador, número de muestras, latencia al arrastrar y percentil 95 del tiempo de fotograma. Como objetivo inicial usar 33 ms por fotograma y 100 ms de respuesta visual durante el arrastre. Ajustar detalle gráfico antes que precisión matemática; medir de nuevo y registrar diferencias. |

La animación corresponde a las gráficas del área de trabajo y al laboratorio. El menú serio permanece estático. Reutilizá las fases [del visor](02-interfaz.md), [del laboratorio](06-kepler.md) y [de ampliaciones](07-libros.md). El registro de cobertura debe identificar operaciones, casos no admitidos y plataformas verificadas.

## Evidencia integrada

| Fase | Alcance de esta entrega |
| --- | --- |
| Q01–Q03 | Se reutilizaron los casos de las 22 sesiones y de Cálculo I y II de [COBERTURA](../COBERTURA.md). Las nuevas comprobaciones independientes cubren la regla de la cadena, la restricción de `ln(x²−1)`, el planteamiento de una región y una arandela, el cruce racional de dos rectas y el último punto de Newton con su motivo y residuo. |
| Q04 | El punto de la segunda recta permite cambiar su término independiente. Al soltarlo o pulsar Enter en el campo, Python actualiza ecuaciones, cruce exacto y clasificación. La cámara ofrece desplazamiento, zoom y restablecimiento. Los planos permiten girar y ampliar la vista. |
| Q05 | Las escenas de tangente, área y arandelas enlazan el control con el dibujo, los valores y la fórmula KaTeX del mismo estado. Para la tangente se muestran las muestras válidas entre −4 y 4, con cortes en las discontinuidades. Si el dominio no se puede representar con intervalos comprobados, se conserva la respuesta simbólica. |
| Q06 | El reloj común de Kepler incorpora 0,5×, 1× y 2×. Al cambiar velocidad durante la reproducción se conserva el instante actual. También se conserva el control de pausa y paso a paso existente. |
| Q07 | Se agruparon 120 eventos de puntero en 30 redibujos. En Qt WebEngine 6.10.2, Linux x86-64 y Xeon Platinum 8573C, la latencia visual P95 fue 22,6 ms a 1366 px y 16,7 ms a 390 px. El tiempo P95 por fotograma fue 16,8 y 16,7 ms. Los recorridos verificaron 65 muestras de tangente, 66 puntos de área y 65 secciones de arandela. La segunda resolución se simuló en el mismo equipo. Quedan pendientes las mediciones en dispositivos físicos. |

Para reproducir el recorrido gráfico, ejecutá `python -m pruebas.entrega.interfaz --calidad --ancho 1366` y repetilo con `--ancho 390`. El arranque web se verifica con `python -m plataformas.verificar_web --directorio build/web --prefijo`.

## Cierre del arranque y contraste

La barra permanece desde el primer paso hasta que está disponible el editor, el resultado o el reloj de Kepler. Muestra cinco pasos en un arranque completo, el avance estimado, el paso siguiente, el tiempo transcurrido y el restante cuando puede estimarse. Go Live muestra también el número de recursos pendientes cuando el trabajador conoce el total. Al terminar se oculta. Un fallo deja un mensaje breve y **Reintentar**. La preparación automática de un cálculo termina en silencio.

Se verificó el paquete estático bajo `/Synapsis/`, incluyendo la carga de un editor lento y el reintento tras un fallo del motor. El ámbar se usa en la barra, la acción principal y la selección activa del área de trabajo. La variante oscura del mismo tono conserva el contraste en el modo claro.

Se repitió Q04–Q07 en Qt WebEngine 6.10.2 a 1366 y 390 px. En ambas vistas los 120 eventos produjeron 30 redibujos. El P95 de respuesta fue 23,8 y 16,7 ms respectivamente, con P95 de fotograma de 16,8 ms. El ancho móvil se simuló en el mismo equipo Linux. Las mediciones en dispositivos físicos quedan pendientes.
