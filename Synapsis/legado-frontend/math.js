const EPSILON = 1e-12;
const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;
const numberFormat = new Intl.NumberFormat('es-NI', { maximumSignificantDigits: 9, useGrouping: false });

export function format(value) {
  if (typeof value !== 'number') return String(value);
  if (!Number.isFinite(value)) return 'indefinido';
  const magnitude = Math.abs(value);
  if (magnitude && (magnitude < 1e-5 || magnitude >= 1e9)) return value.toExponential(5);
  return numberFormat.format(Object.is(value, -0) ? 0 : value);
}

export function scalar(text, label = 'el valor') {
  const parts = String(text ?? '').trim().replaceAll('−', '-').split('/').map(part => part.trim());
  if (parts.length > 2 || !parts.every(part => decimal.test(part))) {
    throw new Error(`Ingresá un número válido para ${label}.`);
  }
  const value = Number(parts[0]) / (parts.length === 2 ? Number(parts[1]) : 1);
  if (!Number.isFinite(value) || Math.abs(value) > 1e12) {
    throw new Error(`${label} debe ser un número finito entre −10¹² y 10¹².`);
  }
  return value;
}

export function vector(text, label) {
  const values = String(text ?? '').trim().split(/[\s,]+/).filter(Boolean);
  if (!values.length || values.length > 12) throw new Error(`${label} debe tener entre 1 y 12 componentes.`);
  return values.map(value => scalar(value, label));
}

export function matrix(text, label) {
  const rows = String(text ?? '').trim().split(/[\n;]+/).filter(row => row.trim());
  if (!rows.length || rows.length > 12) throw new Error(`${label} debe tener entre 1 y 12 filas.`);
  const values = rows.map(row => vector(row, label));
  if (values.some(row => row.length !== values[0].length)) {
    throw new Error(`Todas las filas de ${label} deben tener la misma cantidad de números.`);
  }
  return values;
}

function eliminate(matrix, columns, reduced, record = false) {
  const rows = matrix.map(row => [...row]);
  const pivots = [];
  const steps = [];
  const scales = rows.map(row => Math.max(...row.slice(0, columns).map(Math.abs)));
  const rightScale = rows.map(row => Math.abs(row[columns] ?? 0));
  let determinant = 1;
  const note = description => { if (record) steps.push(description); };

  for (let col = 0, head = 0; col < columns && head < rows.length; col++) {
    let selected = head;
    let best = 0;
    for (let row = head; row < rows.length; row++) {
      const ratio = scales[row] ? Math.abs(rows[row][col]) / scales[row] : 0;
      if (ratio > best) {
        best = ratio;
        selected = row;
      }
    }
    if (best <= EPSILON) continue;
    if (selected !== head) {
      [rows[selected], rows[head]] = [rows[head], rows[selected]];
      [scales[selected], scales[head]] = [scales[head], scales[selected]];
      [rightScale[selected], rightScale[head]] = [rightScale[head], rightScale[selected]];
      determinant *= -1;
      note(`Intercambiar F${head + 1} y F${selected + 1}.`);
    }
    const pivot = rows[head][col];
    determinant *= pivot;
    if (reduced && pivot !== 1) {
      rows[head] = rows[head].map(value => value / pivot);
      rightScale[head] /= Math.abs(pivot);
      note(`Dividir F${head + 1} por ${format(pivot)}.`);
    }
    for (let row = reduced ? 0 : head + 1; row < rows.length; row++) {
      if (row === head || rows[row][col] === 0) continue;
      const factor = rows[row][col] / rows[head][col];
      rows[row] = rows[row].map((value, index) => value - factor * rows[head][index]);
      rows[row][col] = 0;
      rightScale[row] += Math.abs(factor) * rightScale[head];
      note(`F${row + 1} ← F${row + 1} − (${format(factor)}) × F${head + 1}.`);
    }
    pivots.push(col);
    head++;
  }

  if (rows.some(row => row.some(value => !Number.isFinite(value)))) {
    throw new Error('La escala de los datos desbordó la precisión numérica disponible.');
  }
  return { rows, pivots, determinant: pivots.length === columns ? determinant : 0, steps, rightScale };
}

const group = (title, rows, headings) => ({ title, rows, headings });
const xname = index => `x${index + 1}`;
const dot = (a, b) => a.reduce((sum, value, index) => sum + value * b[index], 0);

export function linearSystem(data) {
  const input = matrix(data.matrix, 'la matriz aumentada');
  const size = input[0].length - 1;
  if (size < 1) throw new Error('Agregá al menos un coeficiente y un término independiente por fila.');

  const useGauss = data.method === 'gauss';
  const jordan = eliminate(input, size, true, !useGauss && data.steps);
  const view = useGauss ? eliminate(input, size, false, data.steps) : jordan;
  const rank = jordan.pivots.length;
  const inconsistent = jordan.rows.slice(rank).some((row, index) => Math.abs(row[size]) > EPSILON * jordan.rightScale[index + rank]);
  const fullRank = rank + Number(inconsistent);
  const unique = !inconsistent && rank === size;
  const free = Array.from({ length: size }, (_, index) => index).filter(index => !jordan.pivots.includes(index));
  const result = {
    main: inconsistent ? 'Sistema incompatible' : unique ? 'Solución única' : 'Infinitas soluciones',
    groups: [],
  };

  if (data.ranks) result.note = `Rango de A = ${rank}. Rango de [A | b] = ${fullRank}.`;
  if (data.solution && !inconsistent) {
    const rows = jordan.pivots.map((index, row) => {
      const equation = [format(jordan.rows[row][size])];
      free.forEach((variable, parameter) => {
        const factor = -jordan.rows[row][variable];
        if (factor) equation.push(`${factor < 0 ? '−' : '+'} ${Math.abs(factor) === 1 ? '' : format(Math.abs(factor)) + '·'}t${parameter + 1}`);
      });
      return [xname(index), equation.join(' ')];
    });
    free.forEach((variable, parameter) => rows.push([xname(variable), `t${parameter + 1} ∈ ℝ`]));
    result.groups.push(group('Solución', rows, ['Variable', 'Valor']));
  }
  if (data.form) {
    const headings = Array.from({ length: size }, (_, index) => xname(index));
    result.groups.push(group(useGauss ? 'Forma escalonada' : 'Forma escalonada reducida', view.rows, [...headings, 'b']));
  }
  if (data.steps) result.steps = view.steps.length ? view.steps : ['La matriz ya está en la forma solicitada.'];
  return result;
}

export function matrixOperations(data) {
  const a = matrix(data.a, 'A');
  const width = a[0].length;
  const { op } = data;
  if (op === 'determinante' || op === 'inversa') {
    if (a.length !== width) throw new Error('Esta operación requiere una matriz cuadrada.');
    if (op === 'determinante') return { main: `det(A) = ${format(eliminate(a, width, false).determinant)}` };
    const identity = a.map((row, i) => [...row, ...Array.from({ length: width }, (_, j) => Number(i === j))]);
    const answer = eliminate(identity, width, true);
    if (answer.pivots.length !== width) throw new Error('La matriz es singular. Su inversa no existe.');
    return { main: 'Inversa de A', groups: [group('A⁻¹', answer.rows.map(row => row.slice(width)))] };
  }
  if (op === 'transpuesta') {
    return { main: 'Transpuesta de A', groups: [group('Aᵀ', a[0].map((_, col) => a.map(row => row[col])))] };
  }
  const b = matrix(data.b, 'B');
  if (op === 'producto') {
    if (width !== b.length) throw new Error('Las columnas de A deben coincidir con las filas de B.');
    return { main: 'Producto de matrices', groups: [group('A × B', a.map(row => b[0].map((_, col) => dot(row, b.map(bRow => bRow[col])))))] };
  }
  if (a.length !== b.length || width !== b[0].length) throw new Error('A y B deben tener las mismas dimensiones.');
  const sign = op === 'suma' ? 1 : -1;
  return { main: op === 'suma' ? 'Suma de matrices' : 'Resta de matrices', groups: [group(sign > 0 ? 'A + B' : 'A − B', a.map((row, i) => row.map((value, j) => value + sign * b[i][j])))] };
}

export function vectorOperations(data) {
  const a = vector(data.a, 'u');
  if (data.op === 'norma') return { main: `‖u‖ = ${format(Math.hypot(...a))}` };
  const b = vector(data.b, 'v');
  if (a.length !== b.length) throw new Error('Los vectores deben tener la misma dimensión.');
  if (data.op === 'punto') return { main: `u · v = ${format(dot(a, b))}` };
  if (data.op === 'angulo') {
    const norm = Math.hypot(...a) * Math.hypot(...b);
    if (!norm) throw new Error('El ángulo con un vector nulo no está definido.');
    const cosine = Math.min(1, Math.max(-1, dot(a, b) / norm));
    return { main: `θ = ${format(Math.acos(cosine) * 180 / Math.PI)}°` };
  }
  if (data.op === 'cruz') {
    if (a.length !== 3) throw new Error('El producto cruz requiere vectores de tres componentes.');
    return { main: 'Producto cruz', groups: [group('u × v', [[a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]])] };
  }
  const alpha = data.op === 'combinacion' ? scalar(data.alpha, 'α') : 1;
  const beta = data.op === 'combinacion' ? scalar(data.beta, 'β') : 1;
  return { main: data.op === 'combinacion' ? 'Combinación lineal' : 'Suma de vectores', groups: [group('Vector resultante', [a.map((value, index) => alpha * value + beta * b[index])])] };
}

const functions = {
  sin: Math.sin, sen: Math.sin, cos: Math.cos, tan: Math.tan, asin: Math.asin,
  acos: Math.acos, atan: Math.atan, abs: Math.abs, sqrt: Math.sqrt, exp: Math.exp,
  ln: Math.log, log: Math.log10,
};

export function expression(source, variable = 'x') {
  const text = String(source ?? '').toLowerCase().replaceAll('π', 'pi').replaceAll('−', '-').replaceAll('×', '*').replaceAll('÷', '/');
  if (!text.trim() || text.length > 180) throw new Error('La expresión debe tener entre 1 y 180 caracteres.');
  const tokens = text.match(/(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?|[a-z]+|[^\s]/g);
  let cursor = 0;
  const take = token => tokens[cursor] === token && Boolean(++cursor);
  const require = token => {
    if (!take(token)) throw new Error(`Falta «${token}» en la expresión.`);
  };
  const operations = {
    '+': (a, b) => a + b, '-': (a, b) => a - b,
    '*': (a, b) => a * b, '/': (a, b) => a / b,
  };
  function series(read, allowed) {
    let left = read();
    while (allowed.includes(tokens[cursor])) {
      const op = operations[tokens[cursor++]];
      const a = left;
      const b = read();
      left = x => op(a(x), b(x));
    }
    return left;
  }
  function primary() {
    if (take('(')) {
      const result = sum();
      require(')');
      return result;
    }
    const token = tokens[cursor++];
    if (token === variable) return x => x;
    if (token === 'pi') return () => Math.PI;
    if (token === 'e') return () => Math.E;
    if (decimal.test(token ?? '')) return () => Number(token);
    if (Object.hasOwn(functions, token)) {
      require('(');
      const value = sum();
      require(')');
      return x => functions[token](value(x));
    }
    throw new Error(`Elemento inválido en la expresión: ${token ?? 'fin de la expresión'}.`);
  }
  function signed() {
    if (take('+')) return signed();
    if (take('-')) {
      const value = signed();
      return x => -value(x);
    }
    const base = primary();
    if (!take('^')) return base;
    const power = signed();
    return x => base(x) ** power(x);
  }
  const sum = () => series(() => series(signed, ['*', '/']), ['+', '-']);
  const result = sum();
  if (cursor < tokens.length) throw new Error('Revisá la expresión y escribí las multiplicaciones con *.');
  return result;
}

export function graph(data) {
  const from = scalar(data.from, 'el límite inicial');
  const to = scalar(data.to, 'el límite final');
  if (to <= from) throw new Error('El límite final debe ser mayor que el inicial.');
  const parametric = data.type === 'parametrica';
  const x = parametric ? expression(data.expr, 't') : t => t;
  const y = expression(parametric ? data.y : data.expr, parametric ? 't' : 'x');
  const evaluate = t => [x(t), y(t)];
  const points = Array.from({ length: 701 }, (_, i) => evaluate(from + i * (to - from) / 700));
  if (!points.some(point => point.every(Number.isFinite))) throw new Error('La curva no tiene valores reales finitos en este intervalo.');
  const sample = Array.from({ length: 5 }, (_, i) => {
    const t = from + i * (to - from) / 4;
    return parametric ? [t, ...evaluate(t)] : evaluate(t);
  });
  return {
    main: parametric ? 'Curva paramétrica' : 'Gráfica de y = f(x)',
    plot: { points, parametric },
    groups: [group('Puntos de referencia', sample, parametric ? ['t', 'x(t)', 'y(t)'] : ['x', 'f(x)'])],
  };
}

function iterationInputs(data) {
  const tolerance = scalar(data.tolerance, 'la tolerancia');
  const limit = scalar(data.limit, 'el máximo de iteraciones');
  if (tolerance <= 0 || tolerance >= 1 || !Number.isInteger(limit) || limit < 1 || limit > 200) {
    throw new Error('Usá una tolerancia entre 0 y 1 y un máximo de 1 a 200 iteraciones.');
  }
  return { tolerance, limit };
}

export function roots(data) {
  const f = expression(data.expr);
  const { tolerance, limit } = iterationInputs(data);
  const bracket = data.method === 'biseccion' || data.method === 'posicion';
  const newton = data.method === 'newton';
  const slope = newton && data.derivative?.trim() ? expression(data.derivative) : x => {
    const step = Math.cbrt(Number.EPSILON) * Math.max(1, Math.abs(x));
    return (f(x + step) - f(x - step)) / (2 * step);
  };
  let a = scalar(data.a, bracket ? 'a' : 'x₀');
  let b = newton ? a : scalar(data.b, bracket ? 'b' : 'x₁');
  const evaluate = x => {
    const value = f(x);
    if (!Number.isFinite(x) || !Number.isFinite(value)) throw new Error('La función salió de su dominio real durante el cálculo.');
    return value;
  };
  let fa = evaluate(a);
  let fb = newton ? fa : evaluate(b);
  const rows = [];
  let converged = false;
  if (bracket && a >= b) throw new Error('El intervalo requiere a < b.');
  if (Math.abs(fa) <= tolerance || Math.abs(fb) <= tolerance) {
    const startIsRoot = Math.abs(fa) <= tolerance;
    b = startIsRoot ? a : b;
    fb = startIsRoot ? fa : fb;
    rows.push([0, b, fb]);
    converged = true;
  } else if (bracket && Math.sign(fa) === Math.sign(fb)) {
    throw new Error('La función debe cambiar de signo entre a y b para usar este método.');
  }
  for (let k = 1; k <= limit && !converged; k++) {
    let x;
    if (data.method === 'biseccion') {
      x = a + (b - a) / 2;
    } else if (newton) {
      const d = slope(b);
      if (!Number.isFinite(d) || d === 0) throw new Error('La derivada es nula o indefinida en una iteración.');
      x = b - fb / d;
    } else {
      const denominator = fb - fa;
      if (!denominator) throw new Error('Dos evaluaciones coinciden. Probá otros valores iniciales.');
      x = b - (fb / denominator) * (b - a);
    }
    const fx = evaluate(x);
    rows.push([k, x, fx]);
    converged = Math.abs(fx) <= tolerance;
    if (converged || k === limit) {
      b = x;
      fb = fx;
    } else if (bracket) {
      if (Math.sign(fx) === Math.sign(fa)) {
        a = x;
        fa = fx;
      } else {
        b = x;
        fb = fx;
      }
    } else {
      a = b;
      fa = fb;
      b = x;
      fb = fx;
    }
  }
  return {
    main: converged ? `Raíz aproximada: ${format(b)}` : `Última aproximación: ${format(b)}`,
    note: converged ? `Residuo |f(x)| = ${format(Math.abs(fb))}.` : 'Se alcanzó el límite de iteraciones sin cumplir la tolerancia.',
    groups: [group('Iteraciones', rows, ['k', 'xₖ', 'f(xₖ)'])],
  };
}

export function linearIteration(data) {
  const input = matrix(data.matrix, 'la matriz aumentada');
  const size = input.length;
  if (input.some(row => row.length !== size + 1)) throw new Error('Ingresá una matriz aumentada de n × (n + 1).');
  if (input.some((row, i) => row[i] === 0)) throw new Error('La diagonal contiene un cero. Reordená las ecuaciones y probá de nuevo.');
  let value = data.start?.trim() ? vector(data.start, 'el vector inicial') : Array(size).fill(0);
  if (value.length !== size) throw new Error('El vector inicial debe tener una componente por incógnita.');
  const { tolerance, limit } = iterationInputs(data);
  const residual = x => Math.max(...input.map(row => Math.abs(dot(row.slice(0, size), x) - row[size])));
  let error = residual(value);
  let converged = error <= tolerance;
  const rows = [[0, ...value, error]];
  for (let k = 1; k <= limit && !converged; k++) {
    const next = [...value];
    for (let i = 0; i < size; i++) {
      const row = input[i];
      const source = data.method === 'seidel' ? next : value;
      const sum = source.reduce((acc, v, col) => col === i ? acc : acc + row[col] * v, 0);
      next[i] = (row[size] - sum) / row[i];
    }
    error = residual(next);
    if (!Number.isFinite(error)) break;
    rows.push([k, ...next, error]);
    value = next;
    converged = error <= tolerance;
  }
  return {
    main: converged ? 'El método convergió' : 'Convergencia sin confirmar',
    note: converged ? `Residuo máximo: ${format(error)}.` : 'La aproximación no cumplió la tolerancia con estos datos y límite.',
    groups: [group('Último vector calculado', [value], value.map((_, i) => xname(i))),
      group('Iteraciones', rows, ['k', ...value.map((_, i) => xname(i)), 'Residuo'])],
  };
}

export function numericalErrors(data) {
  const exact = scalar(data.exact, 'el valor exacto');
  const approximation = scalar(data.approx, 'la aproximación');
  const absolute = Math.abs(exact - approximation);
  const relative = exact === 0 ? NaN : absolute / Math.abs(exact);
  return {
    main: `Error absoluto: ${format(absolute)}`,
    note: exact === 0 ? 'El error relativo y porcentual son indefinidos cuando el valor exacto es 0.' : undefined,
    groups: [group('Medidas de error', [
      ['Absoluto', absolute], ['Relativo', relative], ['Porcentual', exact === 0 ? 'Indefinido' : `${format(relative * 100)} %`],
    ], ['Medida', 'Valor'])],
  };
}

const romanDigits = [[1000,'M'],[900,'CM'],[500,'D'],[400,'CD'],[100,'C'],[90,'XC'],[50,'L'],[40,'XL'],[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];

function roman(value) {
  if (value < 1 || value > 3999) throw new Error('Usá un número entero del 1 al 3999 para los romanos.');
  let result = '';
  for (const [digit, symbol] of romanDigits) {
    while (value >= digit) {
      result += symbol;
      value -= digit;
    }
  }
  return result;
}

export function numberSystems(data) {
  const text = String(data.value ?? '').trim().toUpperCase();
  if (data.op === 'romano') {
    if (!/^\d{1,5}$/.test(text)) throw new Error('Ingresá un entero decimal del 1 al 3999.');
    return { main: roman(Number(text)), note: `${Number(text)} en números romanos.` };
  }
  if (data.op === 'decimal') {
    if (!/^[IVXLCDM]{1,15}$/.test(text)) throw new Error('Ingresá un número romano válido.');
    let remaining = text;
    let result = 0;
    for (const [digit, symbol] of romanDigits) {
      while (remaining.startsWith(symbol)) {
        result += digit;
        remaining = remaining.slice(symbol.length);
      }
    }
    if (remaining || roman(result) !== text) throw new Error('Ingresá una cifra romana en su forma estándar, por ejemplo XLIX.');
    return { main: String(result), note: `${text} en el sistema decimal.` };
  }
  const from = scalar(data.from, 'la base de origen');
  const to = scalar(data.to, 'la base de destino');
  if (![from, to].every(base => Number.isInteger(base) && base >= 2 && base <= 36)) {
    throw new Error('Las bases deben ser números enteros entre 2 y 36.');
  }
  if (!/^[+-]?[A-Z0-9]{1,96}$/.test(text)) throw new Error('Ingresá un entero de hasta 96 dígitos sin separadores.');
  let value = 0n;
  for (const char of text.replace(/^[+-]/, '')) {
    const digit = parseInt(char, 36);
    if (digit >= from) throw new Error(`El dígito ${char} no existe en base ${from}.`);
    value = value * BigInt(from) + BigInt(digit);
  }
  if (text.startsWith('-')) value = -value;
  return { main: value.toString(to).toUpperCase(), note: `${text} en base ${from}, convertido a base ${to}.` };
}
