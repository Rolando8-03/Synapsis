// Notación lineal para el analizador de Python. El cálculo y el dominio siguen en el motor.
const functions = new Set(['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sqrt', 'ln', 'log', 'exp', 'abs', 'factorial']);
const constants = new Set(['pi', 'e', 'Ans']);

export function explicitProducts(source, visual = false, variables = ['x']) {
  source = source.replaceAll('π', 'pi').replaceAll('×', '*').replaceAll('÷', '/').replaceAll('−', '-');
  const tokens = source.matchAll(/(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[a-zA-Z]+|\*\*|\S/g);
  const output = [];
  let previous = '';
  let previousKind = '';
  let beforePrevious = '';
  for (const {0: token, index} of tokens) {
    let kind;
    if (/^[\d.]/.test(token) && token !== '.') kind = 'number';
    else if (functions.has(token)) kind = 'function';
    else if (constants.has(token) || variables.includes(token)) kind = 'symbol';
    else if (['+', '-', '*', '/', '^', '(', ')', '**'].includes(token)) kind = token;
    else throw new Error(`Revisá «${token}» en «${source.slice(Math.max(0, index - 5), index + token.length + 5)}». Usá ${variables.join(' o ')} como variable y × para separar factores.`);

    if (visual && kind === 'number' && /e/i.test(token)) {
      throw new Error(`Aclará «${token}» usando × para el factor e o una potencia de 10 para notación científica.`);
    }
    if (previousKind === 'function' && kind !== '(') {
      throw new Error(`Encerrá el argumento de ${previous} entre paréntesis.`);
    }
    const joinsFactors = ['number', 'symbol', ')'].includes(previousKind)
      && ['number', 'symbol', 'function', '('].includes(kind);
    if (joinsFactors) {
      if (beforePrevious === '/' || (previousKind === 'number' && kind === 'number')) {
        throw new Error(`Aclará el producto cerca de «${previous} ${token}» con × o agrupá el denominador con paréntesis.`);
      }
      output.push('*');
    }
    output.push(token);
    beforePrevious = previous;
    previous = token;
    previousKind = kind;
  }
  if (previousKind === 'function') throw new Error(`Completá el argumento de ${previous} entre paréntesis.`);
  return output.join('');
}

export function calculusIntent(source) {
  if (/^(?:\\int(?![A-Za-z])|∫)/u.test(source.trim())) return 'integral';
  if (/^(?:\\lim(?![A-Za-z])|lim\s*_)/u.test(source.trim())) return 'limite';
  if (/^(?:\\frac\s*\{\s*d\s*\}\s*\{\s*d[a-z]\s*\}|d\s*\/\s*d[a-z]\b)/u.test(source.trim())) return 'derivada';
  return '';
}

function readScript(source) {
  if (!source.startsWith('{')) return [source[0] ?? '', source.slice(1)];
  let open = 1;
  for (let i = 1; i < source.length; i++) {
    if (source[i] === '{') open++;
    if (source[i] === '}' && --open === 0) return [source.slice(1,i), source.slice(i+1)];
  }
  throw new Error('Completá el dato dentro de la plantilla.');
}

export function calculusNotation(source) {
  source = source.trim().replace(/\\(?:displaystyle|,|!|;|:|quad|qquad)\s*/g,'');
  const operacion = calculusIntent(source);
  if (!operacion) return {expresion:source};
  if (operacion === 'integral') {
    let body = source.replace(/^(?:\\int(?![A-Za-z])|∫)\s*/u,'');
    const bounds = {};
    while (body.startsWith('_') || body.startsWith('^')) {
      const name = body[0] === '_' ? 'inferior' : 'superior';
      [bounds[name], body] = readScript(body.slice(1).trimStart());
      if (!bounds[name]) throw new Error('Completá los límites de integración.');
      body = body.trimStart();
    }
    const differential = /(?:\\mathrm\{d\}|d)\s*([a-z])\s*$/.exec(body);
    if (!differential) throw new Error('Escribí el diferencial al final, por ejemplo dx.');
    return {operacion, ...bounds, variable:differential[1], expresion:body.slice(0,differential.index).trim()};
  }
  if (operacion === 'limite') {
    const body = source.replace(/^(?:\\lim|lim)\s*_?\s*/u,'');
    const [condition, expression] = readScript(body);
    const approach = /^\s*([a-z])\s*(?:\\(?:to|rightarrow)(?![A-Za-z])|→|->)\s*(.+)$/u.exec(condition);
    if (!approach) throw new Error('Indicá a qué punto se aproxima x en el límite.');
    const side = /\^\{?([+-])\}?$/.exec(approach[2]);
    const point = (side ? approach[2].slice(0,side.index) : approach[2]).trim();
    const infinity = /^([+-]?)\\infty$/u.exec(point);
    return {operacion, variable:approach[1], expresion:expression.trim(),
      ...(infinity ? {tecnica_limite:'al_infinito', lado:infinity[1] === '-' ? '-' : '+'}
        : {punto:point, lado:side?.[1] ?? 'ambos'})};
  }
  const operator = /^(?:\\frac\s*\{\s*d\s*\}\s*\{\s*d([a-z])\s*\}|d\s*\/\s*d([a-z])\b)/u.exec(source);
  return {operacion, variable:operator[1] ?? operator[2], expresion:source.slice(operator[0].length).trim()};
}
