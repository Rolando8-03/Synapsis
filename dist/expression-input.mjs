// Notación lineal para el analizador de Python. El cálculo y el dominio siguen en el motor.
const functions = new Set(['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sqrt', 'ln', 'log', 'exp', 'abs', 'factorial']);
const symbols = new Set(['x', 'pi', 'e', 'Ans']);

export function explicitProducts(source, visual = false) {
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
    else if (symbols.has(token)) kind = 'symbol';
    else if (['+', '-', '*', '/', '^', '(', ')', '**'].includes(token)) kind = token;
    else throw new Error(`Revisá «${token}» en «${source.slice(Math.max(0, index - 5), index + token.length + 5)}». Usá x como variable y × para separar factores.`);

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
