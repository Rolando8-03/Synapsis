# Un laboratorio para las tres leyes de Kepler

Reutilizá `eccentric_anomaly`, `point`, `sector` y la caché de `kepler.py` donde correspondan. `dist/orbit.js` controla hoy tres experimentos independientes. Conservá la ruta vigente durante la transición. Cada fase se integra en main. Exponer la escena nueva cuando las tres leyes funcionen juntas.

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
