# Cálculo II

Fuente: [sílabo, clases y exámenes de las 16 semanas](https://drive.google.com/drive/folders/1JqCeunddZXOY5dnNpwHVyrtOO6L4BRis). El [segundo corte](https://docs.google.com/document/d/13hz6jk7bKB29UIQk0-r7A43QXYue1mwJ/edit) exige poder plantear sin evaluar. Trabajá con una familia de ejercicios a la vez. Agregá al catálogo solo lo que tenga desarrollo y validación.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| I01 | Desarrollar una primitiva elemental. | Mostrar regla, coeficiente y constante C. Verificar por derivación en cada intervalo del dominio. |
| I02 | Integrar por sustitución. | Mostrar u, du, ajuste y retorno a x. En una definida cambiar los límites o regresar a x antes de evaluar. |
| I03 | Integrar por partes. | Para $xe^x$ mostrar elección de u y dv, cálculo de du y v, sustitución, simplificación y comprobación. |
| I04 | Resolver fracciones parciales con factores lineales simples. | Para $1/[x(x+1)]$ mostrar factorización, identidad, sistema para coeficientes, logaritmos y restricciones. |
| I05 | Extender fracciones parciales un tipo por sesión. | Validar división previa, factor repetido y cuadrático irreducible en fases independientes. Reconstruir el numerador antes de integrar. |
| I06 | Aplicar una identidad trigonométrica por sesión. | Desarrollar un caso de potencias seno/coseno, después tangente/cotangente y secante/cosecante. Explicar paridad y factor reservado. |
| I07 | Desarrollar una sustitución trigonométrica. | Una familia por sesión para radicales con $a^2-x^2$, $a^2+x^2$ y $x^2-a^2$. Verificar intervalo, signo y retorno a x. |
| I08 | Aplicar el teorema fundamental. | Mostrar primitiva y evaluación en extremos. En $1/x$ sobre [−1,1] detectar singularidad interior antes de evaluar. |
| I09 | Construir una suma de Riemann. | Mostrar partición, ancho, punto de muestra y suma. El deslizador de n actualiza rectángulos y valores coherentes. |
| I10 | Aplicar cambio neto. | Dada una tasa y dos extremos entregar su integral con unidades. Para obtener valor final pedir además el valor inicial. |
| I11 | Plantear área bajo una curva. | Separar área geométrica de integral con signo cuando la curva cruza el eje. |
| I12 | Plantear área entre curvas. | Para $y=x$ e $y=x^2$ justificar cruces 0 y 1, orden de curvas y terminar en $\int_0^1(x-x^2)\,dx$ si se pide solo plantear. Si hay varias regiones, pedir cuál. |
| I13 | Construir el integrando de discos. | Obtener el radio como distancia al eje indicado. Mover la sección y comprobar $\pi R^2$. |
| I14 | Construir el integrando de arandelas. | Mostrar $\pi(R^2-r^2)$ y justificar radio exterior e interior, también para eje desplazado. |
| I15 | Plantear longitud de arco. | Para un segmento recto contrastar la integral con la distancia entre extremos. |
| I16 | Plantear superficie de revolución. | Mostrar elemento de arco y circunferencia con radio igual a la distancia al eje. Identificar unidades de área. |
| I17 | Obtener masa de una barra. | Reconstruir densidad lineal desde sus extremos y obtener dm; permitir pedir solo masa. |
| I18 | Obtener un momento y el centro de masa. | Explicar origen y brazo de palanca; dividir por masa solo cuando sea distinta de cero. |
| I19 | Obtener el centroide de una lámina uniforme. | Verificar una región simétrica, área y ambos momentos con sus convenciones de ejes. |
| I20 | Plantear trabajo de resorte. | Mostrar fuerza variable, origen de elongación y límites. Evaluar solo a petición. |
| I21 | Plantear trabajo de bombeo. | En un cono invertido obtener radio de la rebanada, volumen, peso y altura de elevación. El peso específico puede quedar simbólico. |

## Evidencia de cierre

Los ejemplos se ejecutan desde **Temario → Cálculo II** y por la misma ruta de cálculo en `pruebas/test_calculo_ii.py`.

| ID | Caso comprobado |
| --- | --- |
| I01 | $1/x$ produce $\ln\lvert x\rvert+C$ con dos intervalos de dominio. Se comprueba la derivada y se indica que cada intervalo admite su propia constante. |
| I02 | Con $u=x^2+1$, la integral de $4x(x^2+1)^3$ sobre $[0,1]$ vale $15/2$. El desarrollo regresa a $x$ antes de evaluar. |
| I03 | $xe^x$ da $(x-1)e^x+C$ con $u$, $du$, $dv$, $v$ y el producto comprobado. |
| I04 | $1/[x(x+1)]$ da $1/x-1/(x+1)$ y conserva las exclusiones $0$ y $-1$. |
| I05-division | $(x^3+2)/[x(x+1)]$ separa el cociente $x-1$ y reconstruye $x^3+2$. |
| I05-repetido | $(x+1)/(x-1)^2$ produce $1/(x-1)+2/(x-1)^2$. |
| I05-cuadratico | $(2x+1)/(x^2+1)$ da $\ln(x^2+1)+\arctan x+C$. Se comprueba también un denominador con coeficiente principal distinto de uno. |
| I06-seno-coseno | $\sin^3x\cos^2x$ reserva un seno. $\sin^2x\cos^2x$ reduce dos potencias pares. |
| I06-tangente-cotangente | $\tan^2 x$ y $\cot^2 x$ dan $\tan x-x+C$ y $-\cot x-x+C$, respectivamente. |
| I06-secante-cosecante | $\sec^2 x$ y $\csc^2 x$ dan $\tan x+C$ y $-\cot x+C$, con sus dominios. |
| I07-diferencia | $\sqrt{4-x^2}$ usa $x=2\sin\theta$ en $[-2,2]$. |
| I07-suma | $\sqrt{4+x^2}$ usa $x=2\tan\theta$ para todo $x$ real. |
| I07-exterior | $\sqrt{x^2-4}$ se verifica en las ramas $x\ge2$ y $x\le-2$. |
| I08 | $\int_0^1 x^2\,dx=1/3$. Se rechaza $1/x$ sobre $[-1,1]$ antes de evaluar extremos. |
| I09 | Para $x^2$ sobre $[0,1]$ con $n=2$, la muestra izquierda da $1/8$, el punto medio $5/16$ y la derecha $5/8$. El deslizador actualiza ancho, muestra, suma y dibujo. |
| I10 | Una tasa $12x$ en m/s sobre $[0,1]$ s da un cambio de $6$ m. Para el valor final se exige la cantidad inicial. |
| I11 | Con $f(x)=x$ sobre $[-1,1]$, el área es $1$ y la integral con signo es $0$. |
| I12 | $y=x$ y $y=x^2$ detectan los cruces $0$ y $1$. «Solo plantear» termina en la integral. Si hay varias regiones se muestra su numeración para elegir. |
| I13 | Por discos con $f(x)=x$ y eje $y=2$, la sección en $x=1/2$ tiene área $9\pi/4$. |
| I14 | Entre $y=x+2$ y $y=x+1$ sobre $[0,1]$ el volumen alrededor de $y=0$ es $4\pi$. Si el eje atraviesa la sección, el radio interior se anula. |
| I15 | $y=3x/4$ sobre $[0,4]$ da longitud $5$, igual a la distancia entre extremos. |
| I16 | $y=x+1$ sobre $[0,1]$ alrededor de $y=0$ da $3\pi\sqrt{2}$ en unidades cuadradas. |
| I17 | Una barra de longitud $3$ con densidades $1$ y $3$ en los extremos tiene masa $6$. |
| I18 | La misma barra da momento $-3/2$ respecto a $x_0=2$ y centro de masa $7/4$. La masa nula deja indefinido el centro. |
| I19 | La región entre $y=1-x^2$ e $y=0$ sobre $[-1,1]$ tiene área $4/3$, momentos $M_x=8/15$ y $M_y=0$, y centroide $(0,2/5)$. |
| I20 | Con $k=12$ y una elongación de $0$ a $1/2$, se plantea $\int_0^{1/2}12x\,dx$. Al pedir el valor se obtiene $3/2$. |
| I21 | Para un cono lleno de altura $4$ y radio $2$, la salida al borde da $16\pi\gamma/3$. Se admite $\gamma$ como parámetro. |

Las operaciones explicitan sus familias de entrada. Las fracciones parciales trabajan con polinomios de coeficientes racionales, denominador de grado hasta ocho, factores lineales racionales y cuadráticos de discriminante negativo simples. Las visualizaciones de Riemann admiten de 1 a 32 rectángulos. La geometría de revolución usa ejes horizontales y fronteras polinómicas. Para arco y superficie de polinomios de grado superior a dos, el valor solicitado se etiqueta como aproximado y se calcula con Simpson adaptativo.
