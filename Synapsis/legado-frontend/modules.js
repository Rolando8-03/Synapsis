import { graph, linearIteration, linearSystem, matrixOperations, numberSystems, numericalErrors, roots, vectorOperations } from './math.js';

const field = (name, label, options = {}) => ({ name, label, ...options });
const select = (name, label, options) => field(name, label, { options, wide: true });
const matrixField = (name, label, condition) => field(name, label, {
  area: true, wide: true, condition, hint: 'Una fila por línea. Separá los valores con espacios o comas. Usá punto para decimales.',
});
const text = (name, label, condition, wide = false) => field(name, label, { condition, wide });
const matrixPair = values => ['suma', 'resta', 'producto'].includes(values.op);
const parametric = values => values.type === 'parametrica';
const bracket = values => ['biseccion', 'posicion'].includes(values.method);
const tolerance = [
  field('tolerance', 'Tolerancia', { initial: '0.000001' }),
  field('limit', 'Máximo de iteraciones', { initial: '60' }),
];

export const modules = {
  sistemas: {
    description: 'Ingresá la matriz aumentada y elegí qué resultados querés ver.',
    fields: [
      select('method', 'Método', [['jordan', 'Gauss-Jordan'], ['gauss', 'Eliminación de Gauss']]),
      matrixField('matrix', 'Matriz aumentada [A | b]'),
    ],
    checks: [
      ['solution', 'Solución', true], ['form', 'Matriz escalonada', true],
      ['ranks', 'Rangos', true], ['steps', 'Pasos', true],
    ],
    example: { matrix: '2 1 -1 8\n-3 -1 2 -11\n-2 1 2 -3' },
    calculate: linearSystem,
  },
  matrices: {
    description: 'Operá con matrices reales y comprobá el resultado.',
    fields: [
      select('op', 'Operación', [
        ['determinante', 'Determinante de A'], ['inversa', 'Inversa de A'], ['transpuesta', 'Transpuesta de A'],
        ['suma', 'A + B'], ['resta', 'A − B'], ['producto', 'A × B'],
      ]),
      matrixField('a', 'Matriz A'), matrixField('b', 'Matriz B', matrixPair),
    ],
    example: { a: '4 7\n2 6', b: '1 3\n2 4' },
    calculate: matrixOperations,
  },
  vectores: {
    description: 'Explorá productos, distancias al origen y combinaciones.',
    fields: [
      select('op', 'Operación', [
        ['punto', 'Producto punto'], ['cruz', 'Producto cruz'], ['norma', 'Norma de u'],
        ['angulo', 'Ángulo entre u y v'], ['suma', 'Suma de vectores'], ['combinacion', 'Combinación αu + βv'],
      ]),
      field('a', 'Vector u', { hint: 'Separá los valores con espacios.' }),
      field('b', 'Vector v', { condition: v => v.op !== 'norma' }),
      text('alpha', 'Coeficiente α', v => v.op === 'combinacion'),
      text('beta', 'Coeficiente β', v => v.op === 'combinacion'),
    ],
    example: { a: '2 -1 3', b: '1 4 -2', alpha: '2', beta: '-1' },
    calculate: vectorOperations,
  },
  grafica: {
    description: 'Dibujá una función o una curva paramétrica en el plano.',
    fields: [
      select('type', 'Tipo de gráfica', [['funcion', 'Función explícita'], ['parametrica', 'Curva paramétrica']]),
      field('expr', v => parametric(v) ? 'x(t)' : 'f(x)', { wide: true, hint: 'Usá * para multiplicar, ^ para potencias y radianes para sin y cos.' }),
      text('y', 'y(t)', parametric, true), text('from', 'Desde'), text('to', 'Hasta'),
    ],
    example: values => parametric(values)
      ? { expr: 'cos(t)', y: 'sin(t)', from: '0', to: '6.28318530718' }
      : { expr: 'sin(x) + x/4', from: '-8', to: '8' },
    calculate: graph,
  },
  raices: {
    description: 'Buscá una raíz real y seguí el recorrido del método iteración por iteración.',
    fields: [
      select('method', 'Método', [['biseccion', 'Bisección'], ['posicion', 'Falsa posición'], ['newton', 'Newton'], ['secante', 'Secante']]),
      field('expr', 'f(x)', { wide: true, hint: 'Por ejemplo, x^3 − x − 2. Usá * para multiplicar.' }),
      field('derivative', 'Derivada f′(x), opcional', { wide: true, optional: true, condition: v => v.method === 'newton', hint: 'Si la dejás vacía se aproxima numéricamente.' }),
      text('a', v => bracket(v) ? 'Extremo a' : 'Valor inicial x₀'),
      text('b', v => bracket(v) ? 'Extremo b' : 'Segundo valor x₁', v => v.method !== 'newton'),
      ...tolerance,
    ],
    example: { expr: 'x^3 - x - 2', derivative: '3*x^2 - 1', a: '1', b: '2' },
    calculate: roots,
  },
  iterativos: {
    description: 'Aproximá la solución de un sistema lineal y compará el residuo de cada iteración.',
    fields: [
      select('method', 'Método', [['jacobi', 'Jacobi'], ['seidel', 'Gauss-Seidel']]),
      matrixField('matrix', 'Matriz aumentada [A | b]'),
      field('start', 'Vector inicial, opcional', { optional: true, wide: true, hint: 'Si lo dejás vacío se empieza con ceros.' }),
      ...tolerance,
    ],
    example: { matrix: '10 -1 2 6\n-1 11 -1 22\n2 -1 10 -10', start: '0 0 0' },
    calculate: linearIteration,
  },
  errores: {
    description: 'Medí cuánto se aparta un valor aproximado del valor de referencia.',
    fields: [text('exact', 'Valor exacto'), text('approx', 'Valor aproximado')],
    example: { exact: '3.14159265358979', approx: '3.14' },
    calculate: numericalErrors,
  },
  bases: {
    description: 'Convertí enteros entre bases de 2 a 36 o trabajá con números romanos.',
    fields: [
      select('op', 'Conversión', [['base', 'Entre bases'], ['romano', 'Decimal a romano'], ['decimal', 'Romano a decimal']]),
      text('value', 'Número', undefined, true),
      text('from', 'Base de origen', v => v.op === 'base'), text('to', 'Base de destino', v => v.op === 'base'),
    ],
    example: v => v.op === 'romano' ? { value: '49' } : v.op === 'decimal' ? { value: 'XLIX' } : { value: '11010110', from: '2', to: '16' },
    calculate: numberSystems,
  },
};
