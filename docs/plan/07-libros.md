# Ampliaciones de los cuatro libros

Estas fases son ampliaciones propuestas para Synapsis. Fuentes de estudio: Grossman, *Álgebra lineal*, 7.ª ed., caps. 5–8; Lay, *Álgebra lineal y sus aplicaciones*, 3.ª ed., caps. 4–7; Poole, *Álgebra lineal. Una introducción moderna*, 3.ª ed., §§1.3, 2.2, 4.5, 5.3 y cap. 7; Chapra y Canale, *Métodos numéricos para ingenieros*, 5.ª ed., caps. 5–6, 9–11, 17–18, 21–23 y 25. Vinculá cada ampliación con la operación del curso que consume sus resultados.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| L01 | Graficar intersecciones de rectas o planos. | Comenzar en 2D con dos rectas editables. En otra sesión enlazar el caso 3D a rangos exactos; para más dimensiones mostrar pivotes. |
| L02 | Visualizar una transformación del plano. | Al mover un vector se actualizan su imagen y las imágenes de la base. En cambio de base mantener fijo el vector geométrico. |
| L03 | Comparar tres normas de un vector. | Para (3,4) obtener 7, 5 y 4; mostrar la bola unitaria correspondiente y enlazar con los iterativos. |
| L04 | Mostrar determinante como área orientada. | Arrastrar una columna hasta la dependencia anula el área; cruzar la otra cambia el signo. |
| L05 | Comparar pivoteo con precisión limitada. | Con el mismo A y b contrastar referencia racional y redondeo simulado con y sin pivoteo; señalar el paso que amplifica el error. |
| L06 | Calcular sensibilidad a perturbaciones de b. | Mostrar norma elegida, número de condición si A es invertible y cambio relativo medido. Separar condicionamiento del error del algoritmo. |
| L07 | Explorar intervalos candidatos a raíces. | Marcar cambios de signo y discontinuidades; una raíz de multiplicidad par puede escapar a la exploración. |
| L08 | Incorporar punto fijo. | Comparar dos despejes para la misma raíz; graficar la iteración, verificar el residuo original y comprobar hipótesis antes de ofrecer cota. |
| L09 | Extender proyección de recta a subespacio. | Mostrar la proyección, el residuo y su ortogonalidad a cada vector de una base. |
| L10 | Agregar Gram–Schmidt. | Mostrar cada proyección y normalización; detectar dependencia antes de dividir. |
| L11 | Construir la QR reducida desde la base ortonormal. | Confirmar $Q^TQ=I$ y $QR=A$. En otra sesión comparar la variante modificada con columnas casi dependientes. |
| L12 | Resolver mínimos cuadrados. | Comprobar $A^Tr=0$ y distinguir cuándo los coeficientes son únicos. Reutilizar QR para columnas independientes. |
| L13 | Obtener valores propios. | Construir y resolver el polinomio característico de una matriz pequeña. Explicitar el cuerpo real o complejo y multiplicidades. |
| L14 | Construir un espacio propio. | Reducir $A-\lambda I$ con el motor actual y verificar cada vector con $Av=\lambda v$. |
| L15 | Decidir diagonalización. | Verificar que los espacios propios aportan una base y comprobar $AP=PD$. Mostrar una matriz defectiva. |
| L16 | Aplicar el teorema espectral. | Para A real simétrica verificar una base propia ortonormal. En otra fase visualizar los ejes de la forma cuadrática. |
| L17 | Agregar el método de la potencia. | Normalizar, explicar la semilla y el autovalor dominante; detener por un criterio que muestre el residuo. |
| L18 | Explorar cadenas de Markov. | Validar probabilidades y convención por columnas; comparar una cadena regular y otra periódica desde el mismo estado inicial. |
| L19 | Visualizar la SVD. | Verificar reconstrucción para una matriz rectangular. En sesiones posteriores añadir truncamiento por rango y compresión de una imagen de ejemplo. |
| L20 | Ajustar una recta por regresión. | Mover un dato actualiza los residuos y su suma cuadrática; reutilizar mínimos cuadrados. |
| L21 | Construir interpolación de Newton. | Con nodos distintos mostrar tabla de diferencias divididas y comprobar todos los valores en sus nodos. |
| L22 | Construir el mismo interpolante con Lagrange. | Exponer cada polinomio base y verificar que ambas formas coinciden. |
| L23 | Agregar spline cúbico natural. | Mostrar condiciones en extremos, continuidad y paso por los nodos. Detectar abscisas repetidas. |
| L24 | Comparar trapecios con el Simpson compuesto existente. | Elegir n, comprobar paridad en Simpson 1/3, mostrar pesos y separar estimación de cota. En otra sesión extender a Romberg. |
| L25 | Derivar con diferencias finitas. | Un esquema por sesión: hacia adelante, atrás y centrado. Variar h y distinguir truncamiento y redondeo. Después añadir extrapolación de Richardson. |
| L26 | Integrar una EDO con Euler. | Paso, pendiente, siguiente punto y contraste con solución conocida; añadir Heun y RK4 en sesiones independientes. |
| L27 | Agregar una aplicación visual por sesión. | Elegir red eléctrica, caminos en grafos o código binario. Vincular cada elemento del dibujo con la ecuación o entrada matricial que representa. |
