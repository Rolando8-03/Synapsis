# Cálculo I

Consultá el [sílabo y las 15 carpetas semanales](https://drive.google.com/drive/folders/1Il00NAIj4MMD0ZBjoeSbZL_BTIFqFKVK). Reutilizá `algorithms/calculo.py` bajo `motor_matematico/`, `procedimientos.calculus_trace` y el visor de pasos. Cada operación nueva debe poder elegirse por sí sola.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| C01 ✓ | Determinar el dominio real de una familia de funciones. | Empezar con racionales. En sesiones sucesivas, radicales y logaritmos. Conservar exclusiones previas a simplificar. |
| C02 ✓ | Exponer composición de funciones. | Mostrar sustitución y exigir que la función interior caiga en el dominio de la exterior. |
| C03 ✓ | Obtener inversa en un intervalo inyectivo. | Para $x^2$ indicar la rama elegida y verificar la composición en su dominio. |
| C04 ✓ | Resolver un límite lateral. | Comparar los dos lados de una función por tramos antes de afirmar un límite bilateral. |
| C05 ✓ | Desarrollar una técnica de límites por sesión. | Empezar con factorización de $(x^2-1)/(x-1)$ en 1. Continuar con racionalización, límites infinitos y al infinito. Justificar la regla usada. |
| C06 ✓ | Comprobar continuidad en un punto. | Comparar valor, límites laterales y límite bilateral; el gráfico complementa la demostración. |
| C07 ✓ | Derivar por definición una potencia sencilla. | Para $x^2$ mostrar el cociente incremental, cancelación para h distinto de cero y paso al límite. |
| C08 ✓ | Desglosar una regla de derivación por sesión. | Para $(x^2+1)^3$ separar interior, exterior y producto. Continuar con producto, cociente, exponenciales, logarítmicas y trigonométricas. |
| C09 ✓ | Calcular derivada implícita. | Derivar ambos miembros de $x^2+y^2=1$, aislar $y'$ y justificar dónde es válido dividir. |
| C10 ✓ | Calcular derivada parcial respecto de una variable elegida. | En $x^2y$ mostrar qué variable permanece constante. En otra sesión encadenar derivadas de orden superior. |
| C11 ✓ | Entregar solo números críticos. | Considerar puntos del dominio con derivada cero o inexistente; $\lvert x\rvert$ incluye cero. |
| C12 ✓ | Construir una tabla de signos por derivada. | En $x^3-3x$ enlazar cada intervalo con crecimiento o concavidad. Exigir cambio de concavidad para inflexión. |
| C13 ✓ | Optimizar en una variable. | En intervalo cerrado comparar candidatos interiores y extremos; poder pedir solo planteamiento. |
| C14 ✓ | Clasificar un crítico en dos variables. | En $x^2-y^2$ justificar el punto silla. Con determinante hessiano nulo indicar prueba inconclusa. |
| C15 ✓ | Modelar una aplicación de tasas por sesión. | Incluir tasa media, instantánea, tasas relacionadas y elasticidad. Identificar variable, unidades e interpretación. |
| C16 ✓ | Verificar un teorema del curso por sesión. | Para Rolle comprobar continuidad, derivabilidad e igualdad de extremos; para valor medio o intermedio usar sus hipótesis propias. Hallar el punto solo al solicitarlo. |
| C17 ✓ | Vincular las operaciones de integral de Cálculo I a Cálculo II. | Antiderivada, definida, sustitución y área abren la misma operación desde ambos temarios. |
| C18 ✓ | Obtener el valor promedio de una función. | Para $f(x)=x^2$ en [0,3] plantear la integral dividida por 3 y verificar el promedio 3; rechazar intervalo de longitud cero. |


## Verificación de la fase

El sílabo de MTM0102 del Grupo 7 se consultó para contrastar los cuatro bloques del curso. Las operaciones se agrupan en Graficadora y se enlazan desde el temario de Cálculo I.

| Fases | Evidencia y alcance |
| --- | --- |
| C01–C03 | Se verificaron los dominios de cocientes, radicales y logaritmos con exclusiones de la expresión original. La composición comprueba el dominio interior y exterior. La inversa acepta funciones afines no constantes y una sola rama de una cuadrática. |
| C04–C06 | Se probaron límites diferentes por tramos, factorización, racionalización, polos y cocientes al infinito. Continuidad compara ambos lados y el valor, con una gráfica local cuando se puede muestrear. |
| C07–C10 | La definición desarrolla el cociente incremental de un polinomio. Hay operaciones separadas para cadena, producto, cociente, exponenciales, logaritmos, trigonométricas, implícita polinómica, parciales y parciales sucesivas. |
| C11–C14 | Se verificaron el crítico de valor absoluto, un caso sin cambio de concavidad, los extremos de una función en intervalo cerrado y la clasificación por hessiano. El modo «Solo plantear» devuelve el objetivo y el intervalo. |
| C15–C16 | Las tasas incluyen media, instantánea, relacionadas y elasticidad. Rolle y los teoremas del valor medio e intermedio verifican sus hipótesis y buscan puntos solo bajo petición. |
| C17–C18 | Cálculo I y II enlazan las mismas rutas de antiderivada, definida, sustitución y área. La sustitución admite ajuste a un polinomio en u y área usa curvas polinómicas con intervalo explícito. Se comprobó el promedio 3 de x² en [0,3] y el rechazo del intervalo degenerado. |

La regresión `test_calculo_i.py` ejecuta estos casos por el mismo despachador de la interfaz.
