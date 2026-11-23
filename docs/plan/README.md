# Plan de implementación de Synapsis

**Integración obligatoria en `main`.** Una fase es una fila identificada en las guías. Ejecutá una sola fila por sesión de trabajo. Cada cierre deja la aplicación utilizable en `main`. Los archivos que agrupan filas son guías de consulta, no lotes de implementación.

## Punto de partida

El alcance empieza en la [versión de Synapsis del 23 de noviembre de 2026](https://github.com/Rolando8-03/Synapsis/tree/47893bdb0ce027c2a72027ffa9dbdc18e7066b82). Usá exclusivamente el árbol de `main` de Synapsis como base de implementación y consultá los materiales de clase y los cuatro libros como referencias matemáticas. La aplicación vive en la raíz y ya incorpora ocho módulos, 91 operaciones, 22 sesiones, la ventana Windows, el modo claro/oscuro azul marino y KaTeX local. El menú de operaciones ya se pliega a iconos y conserva su estado. Resolver reemplaza el formulario y Editar datos lo recupera. Sistemas ya admite matriz aumentada y selección de salidas. Solo LU y Solo PLU aceptan únicamente A. Consultá [uso y ejecución](../../README.md) y [cobertura docente](../../COBERTURA.md).

La traza actual ya desarrolla productos, reducciones, factorizaciones y métodos numéricos. La profundidad cambia según la operación. La regla de la cadena puede quedar resumida en «potencia», algunas primitivas por partes y fracciones parciales fallan, y Newton utiliza reglas propias para derivar. El laboratorio tiene tres experimentos con estados independientes. Las fases siguientes parten de esas diferencias comprobadas.

## Guías y orden sugerido

| Guía | Cuándo usarla |
| --- | --- |
| [01 · Ejecución, arquitectura y créditos](01-ejecucion.md) | Leé una vez. Usá su instrucción breve al empezar cada fase. |
| [02 · Operaciones, modo serio y escritura](02-interfaz.md) | Empezá por U01. El menú serio, el teclado y el visor de pasos tienen fases independientes. |
| [03 · Álgebra y métodos del curso](03-curso.md) | Programas 1–9. Priorizá los casos de examen y los fallos de Newton. |
| [04 · Cálculo I](04-calculo-i.md) | Funciones, límites, derivadas y aplicaciones según el curso. |
| [05 · Cálculo II](05-calculo-ii.md) | Técnicas, integrales definidas y aplicaciones. Incluye entregables de solo planteamiento. |
| [06 · Laboratorio de Kepler](06-kepler.md) | Secuencia K01–K08 sobre un modelo físico y un reloj. Puede avanzar independientemente del teclado. |
| [07 · Ampliaciones de los cuatro libros](07-libros.md) | Operaciones adicionales. Usá el resultado del curso como entrada al tema nuevo. |
| [08 · Verificación y distribución](08-entrega.md) | Aplicá el control correspondiente a cada integración. Para distribución final, cubrí también escritorio y ZIP. |

**Protección de la página principal.** El diseño de la portada animada queda protegido en todas las fases, incluidos composición, tarjetas públicas, navegación, paleta, recursos, río, montañas, nave y movimiento al desplazarse. El rediseño autorizado se limita al menú del modo serio. Si ambos comparten marcado o estilos, aislá los cambios bajo el contenedor del modo serio, del área de trabajo o del laboratorio. Comprobá la portada en escritorio y móvil antes de integrar una fase que toque archivos compartidos.

**Primera sesión sugerida:** U01. Para continuar, abrí únicamente esta página, la guía elegida y los archivos afectados. El historial de `main` identifica las fases concluidas por su ID.

## Qué se conserva y qué falta

| Área | Ya disponible en Synapsis | Trabajo planificado |
| --- | --- | --- |
| Interfaz | Portada, temas, tarjetas completas, iconos, historial y edición en el mismo panel | Menú serio estático y editor matemático visual |
| Álgebra | Matrices aumentadas, clasificación, bases, transformaciones, LU/PLU independientes y verificaciones | Profundizar trazas, teoremas y objetivos parciales |
| Numérico | Bisección, falsa posición, secante, Newton, Jacobi, Gauss-Seidel, SOR, errores y Simpson | Derivación de Newton con SymPy, fallos claros y gráficos recorribles |
| Cálculo | Evaluación, derivada, primitivas admitidas, integral definida y numérica | Cobertura de los dos sílabos y técnicas justificadas |
| Laboratorio | Elipses, sectores y comparación de períodos en vistas independientes | Combinar medidas, reloj y enunciados en una escena |
| Escritorio | Lanzadores Windows, recursos locales y arranque web alternativo | Verificar la distribución completa tras integrar las ampliaciones |

**Dependencias.** Los procedimientos pueden avanzar sobre el visor existente. Usá U05 antes de extender el teclado, U11 antes de sincronizar gráficas, L10 antes de L11 y L11 antes de mínimos cuadrados por QR. Los libros amplían el temario después de validar la operación del curso relacionada.
