# Un laboratorio para las tres leyes de Kepler

La escena combinada usa `motor_matematico/algorithms/kepler.py`, con un reloj para la Tierra y la órbita de prueba. `dist/kepler-camera.js` proyecta las coordenadas físicas para girar y ampliar la vista. El contrato histórico del motor sigue disponible para los casos de paridad.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| K01 | Modelar una órbita elíptica con parámetros físicos. | Un objeto valida semieje a positivo, excentricidad en [0,1), parámetro gravitacional positivo y unidades. Separar reloj físico de coordenadas de pantalla. |
| K02 | Calcular posiciones de dos planetas para un tiempo común. | El Sol ocupa un foco común. Para e=0 la distancia es constante y para e próximo a 1 validar el residuo de la ecuación de Kepler. |
| K03 | Calcular sectores en dos intervalos de igual duración de una órbita. | Comparar áreas de sectores elípticos cerca del perihelio y del afelio, también al cruzar una vuelta. Mostrar duración, área y rapidez. |
| K04 | Medir la tercera ley en la misma salida. | Para igual masa central dominante, $T^2/a^3=4\pi^2/\mu$; duplicar a multiplica T por $2^{3/2}$. Variar e con a fijo conserva T. |
| K05 | Integrar una sola escena con los tres enunciados visibles. | Mostrar juntos los focos, ambos sectores y la comparación de períodos sobre dos elipses. Primera: cada planeta recorre una elipse con el Sol en un foco. Segunda: el radio Sol–planeta barre áreas iguales en tiempos iguales. Tercera: el cuadrado del período es proporcional al cubo del semieje mayor para el mismo cuerpo central dominante. |
| K06 | Conectar un reloj y sus controles a todas las mediciones. | Reproducir, pausar, avanzar, retroceder y arrastrar tiempo conserva sincronía. La lectura está accesible con animación pausada. |
| K07 | Añadir el procedimiento del instante seleccionado. | Con los mismos datos mostrar semieje menor, anomalía, posición, área barrida y período con fórmulas, unidades y sustituciones. |
| K08 | Validar fluidez de la escena combinada. | Medir antes/después con el mismo equipo y parámetros. Reusar muestras al pausar o repetir, descartar respuestas obsoletas al arrastrar y detener repintado al salir. |

## Evidencia de cierre

En **Laboratorio 3D** se abre una sola escena con la Tierra como referencia ($a=1$ UA, $e=0,0167$). La órbita de prueba comienza con $a=2,25$ UA y $e=0,30$. El reloj común abarca 12 años, con pasos de 0,01 y reproducción inicial lenta. **Ver leyes** abre los tres enunciados y **Ajustes** reúne los parámetros, la fecha simulada, el PDF y la pantalla completa. Los ejemplos numéricos de K01–K04 siguen usando los parámetros pedagógicos de las pruebas.

| ID | Caso comprobado |
| --- | --- |
| K01 | Se rechazan semiejes o parámetros gravitacionales no positivos, excentricidades fuera de $[0,1)$ y sistemas de unidades distintos. Las posiciones se calculan en UA y luego se proyectan al dibujo. |
| K02 | Una órbita de $a=2$ UA con $e=0$ mantiene su distancia al Sol. En la elipse se verifica la suma de distancias a los dos focos. Para $e=1-2^{-40}$ se comprueba el residuo de la ecuación de Kepler cerca del perihelio. |
| K03 | Con $e_A=0,55$, los sectores de 0,08 años que terminan en perihelio y afelio barren 0,2099 UA². Sus rapideces finales son 11,6611 y 3,3855 UA/año. Se comprueba también el intervalo $[0,96;1,04]$ al cruzar una vuelta. |
| K04 | Pasar de $a=1$ a $a=2$ UA da un período $2^{3/2}$ veces mayor y mantiene $T^2/a^3=1$ año²/UA³. Cambiar $e$ con $a$ fijo mantiene el período. |
| K05 | Los tres enunciados, las dos trayectorias, los focos, los dos sectores y las mediciones aparecen juntos. La interfaz abre directamente la escena conjunta. |
| K06 | Reproducir, pausar, avanzar, retroceder, volver al perihelio y seleccionar 6,43 años actualizan las dos órbitas y las mediciones con la misma muestra. Con movimiento reducido, los pasos y el deslizador siguen accesibles. |
| K07 | La lectura de 6,43 años usa la misma muestra que el gráfico para desarrollar $b$, $M$, $E$, la posición, la rapidez, el área con $\Delta E$ continuo y el período. |
| K08 | El arrastre realiza una sola solicitud. Volver a parámetros ya cargados reutiliza las muestras. Una respuesta demorada a propósito se descarta después de otro ajuste. En 1,2 s de reproducción se observaron 30 actualizaciones del planeta A. Durante 0,5 s fuera de vista se observaron cero. |

### Medición antes y después de K08

Comparación local en el mismo equipo con Chromium 153 y una ventana de 1360 × 950. Se usó la escena combinada de K07 como base. En ambas versiones se fijó $a_B=2,25$ UA y $e_B=0,30$. Cada corrida aplicó doce valores a $e_A$ de 0,56 a 0,67, separados por 20 ms. Después alternó seis veces entre 0,55 y 0,67. Las duraciones incluyen la espera hasta que el reloj vuelve a estar listo. Se reporta la mediana de tres corridas.

| Medida | K07 | K08 |
| --- | ---: | ---: |
| Solicitudes de escena durante el arrastre | 12 | 1 |
| Duración del arrastre hasta que el reloj está listo | 721 ms | 350 ms |
| Solicitudes en seis cambios entre parámetros ya consultados | 6 | 0 |
| Tiempo mediano para aplicar un ajuste ya consultado | 77,8 ms | 0,2 ms |

Las pruebas de modelo están en [test_kepler.py](../../pruebas/test_kepler.py). Se verificaron además los controles en Chromium y la vista móvil de 390 px. Referencia de los enunciados de las tres leyes en [NASA, Gravity & Mechanics](https://science.nasa.gov/learn/basics-of-space-flight/chapter3-3/).

## Pruebas de la escena 3D

En Chromium a 1440 y 390 píxeles se pausó en 6,43 años y se comprobó que las áreas de los dos sectores eran iguales, el valor de $T^2/a^3$ era 1 en ambas órbitas y las sumas focales eran 2 y 4,5 UA. El giro con arrastre, la rueda y la pinza cambiaron el dibujo sin afectar esas medidas. Cambiar el semieje de prueba a 2 UA dio 2,8284 años y conservó la posición de la Tierra. Se probó la selección por fecha, el avance manual, la pantalla completa y la exportación del instante con el encuadre elegido.
