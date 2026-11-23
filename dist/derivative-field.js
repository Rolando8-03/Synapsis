import { MathfieldElement, convertAsciiMathToLatex, convertLatexToAsciiMath } from './vendor/mathlive/mathlive.min.mjs';
import { math as formula, numericTex } from './math-format.js';
import { explicitProducts } from './expression-input.mjs';
import { node } from './matrix-input.js';

MathfieldElement.fontsDirectory = new URL('./vendor/katex/fonts/', import.meta.url).href;
MathfieldElement.soundsDirectory = null;
MathfieldElement.locale = 'es';

const incomplete = 'Completá el exponente, el numerador, el denominador o el radicando que falta.';

function groupEnd(latex, start) {
  while (/\s/.test(latex[start] ?? '')) start++;
  if (latex[start] !== '{') throw new Error(incomplete);
  let depth = 1;
  for (let i = start + 1; i < latex.length; i++) {
    if (latex[i] === '{') depth++;
    if (latex[i] === '}' && --depth === 0) return i + 1;
  }
  throw new Error(incomplete);
}

function expression(latex, variables) {
  // MathLive puede omitir huecos cuando exporta a texto.
  if (/\\placeholder\b|\{\s*\}/u.test(latex)) throw new Error(incomplete);
  const symbols = latex.replace(/\\(?:m?left|m?right|cdot|times|div|sin|cos|tan|ln|log|exp|pi|frac|sqrt)\b/g, '');
  const unsupported = symbols.match(/\\[a-zA-Z]+|[^a-zA-Z0-9\s.+*^()/{}-]/u);
  if (unsupported) throw new Error(`Revisá «${unsupported[0]}» en el campo de la función. Para otras notaciones, usá la entrada de texto.`);

  // Agrupar la fracción completa, también cuando es el exponente o el divisor.
  const delimiters = [];
  for (const fraction of latex.matchAll(/\\frac\b/g)) {
    const numeratorEnd = groupEnd(latex, fraction.index + fraction[0].length);
    const denominatorEnd = groupEnd(latex, numeratorEnd);
    const wrapped = /\(\s*$/.test(latex.slice(0, fraction.index))
      && /^\s*(?:\\m?right\s*)?\)/.test(latex.slice(denominatorEnd));
    if (!wrapped) delimiters.push([fraction.index, '\\left('], [denominatorEnd, '\\right)']);
  }
  for (const [index, delimiter] of delimiters.sort(([a], [b]) => b - a)) {
    latex = latex.slice(0, index) + delimiter + latex.slice(index);
  }
  const ascii = convertLatexToAsciiMath(latex).trim();
  return explicitProducts(ascii, true, variables);
}

function visualLatex(text, variables) {
  const normalize = s => s.replace(/\s+/g, '').replaceAll('**', '^');
  try {
    const latex = convertAsciiMathToLatex(text.replaceAll('**', '^'));
    if (normalize(expression(latex, variables)) === normalize(explicitProducts(text, false, variables))) return latex;
  } catch { /* Conservá la entrada original si no hay conversión fiel. */ }
  return null;
}

export function expressionField(definition, initial, onChange, {differential, variables = ['x']}) {
  variables = ({parcial:['x', 'y'], sumatoria:['k']})[definition.editor] ?? variables;
  const element = node('div', 'ws-field ws-full-field ws-derivative');
  const label = node('label', '', definition.label);
  const math = new MathfieldElement();
  math.id = `ws-math-${definition.name}`;
  math.setAttribute('aria-label', definition.label);
  math.mathVirtualKeyboardPolicy = 'manual';
  math.smartSuperscript = false;

  const text = node('input');
  text.id = `ws-text-${definition.name}`;
  text.type = 'text';
  text.maxLength = 500;
  text.autocomplete = 'off';
  text.spellcheck = false;

  const keys = node('div', 'ws-power-keys');
  keys.setAttribute('role', 'group');
  keys.setAttribute('aria-label', 'Teclado de expresiones');
  for (const [caption, command, name] of [
    ...variables.map(variable => [variable, ['insert', variable]]), ['□ⁿ', 'moveToSuperscript', 'Exponente'],
    ['□⁄□', ['insert', '\\frac{#0}{#?}'], 'Fracción'],
    ['(□)', ['insert', '\\left(#0\\right)'], 'Paréntesis'],
    ['√□', ['insert', '\\sqrt{#0}'], 'Raíz cuadrada'],
    ...Array.from('1234567890', digit => [digit, ['insert', digit]]),
    ['+', ['insert', '+']], ['−', ['insert', '-']], ['×', ['insert', '\\cdot'], 'Multiplicar'],
    ['⇥', 'moveToNextPlaceholder', 'Siguiente hueco'],
    ['→', 'moveToNextChar', 'Avanzar'], ['⌫', 'deleteBackward', 'Borrar'],
  ]) {
    const key = node('button', 'secondary', caption);
    key.type = 'button';
    if (name) {
      key.title = name;
      key.setAttribute('aria-label', name);
    }
    key.addEventListener('pointerdown', event => event.preventDefault());
    key.addEventListener('click', () => {
      math.focus();
      math.executeCommand(command);
    });
    keys.append(key);
  }
  const toggle = node('button', 'secondary');
  toggle.type = 'button';
  const feedback = node('span', 'ws-field-help');
  feedback.setAttribute('role', 'status');
  element.append(label);
  const operator = node('span');
  if (definition.editor) {
    const row = node('div', 'ws-integral-template');
    row.append(operator, math, text);
    element.append(row);
  } else if (differential) {
    const row = node('div', 'ws-integral-template');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', `Integral indefinida respecto de ${differential}`);
    row.append(formula('\\displaystyle\\int', '∫'), math, text,
      formula(`\\mathrm{d}${differential}`, `d${differential}`));
    element.append(row);
  } else {
    element.append(math, text);
  }
  element.append(keys, toggle, feedback);

  function useVisual(visual) {
    math.hidden = keys.hidden = !visual;
    text.hidden = visual;
    label.htmlFor = visual ? math.id : text.id;
    toggle.textContent = visual ? 'Escribir como texto' : 'Usar editor matemático';
    feedback.hidden = true;
  }

  function set(value) {
    const isText = typeof value === 'string' && value !== '' && value !== definition.default;
    if (isText) text.value = value;
    else math.setValue(typeof value === 'string' ? value : value.latex, {silenceNotifications:true});
    useVisual(!isText);
  }

  let lastVisual;
  toggle.addEventListener('click', () => {
    if (math.hidden) {
      const latex = lastVisual?.text === text.value ? lastVisual.latex : visualLatex(text.value, variables);
      if (latex === null) {
        feedback.textContent = 'Esta expresión se edita como texto. Para empezar una expresión nueva en el editor, vaciá el campo.';
        feedback.hidden = false;
        return;
      }
      math.setValue(latex, {silenceNotifications:true});
      useVisual(true);
      math.focus();
    } else {
      try { text.value = expression(math.value, variables); }
      catch { text.value = math.value; }
      lastVisual = {text: text.value, latex: math.value};
      useVisual(false);
      text.focus();
    }
    onChange();
  });
  element.addEventListener('input', onChange);
  set(initial);
  return {
    definition, element, set,
    updateNotation(values) {
      if (definition.editor === 'parcial') {
        const variable = values.variable === 'y' ? 'y' : 'x';
        operator.replaceChildren(formula(`\\frac{\\partial}{\\partial ${variable}}`, `derivada parcial respecto de ${variable}`));
      }
      if (definition.editor === 'sumatoria') {
        const first = /^-?\d+$/.test(values.inferior) ? values.inferior : 'a';
        const last = /^-?\d+$/.test(values.superior) ? values.superior : 'b';
        operator.replaceChildren(formula(`\\sum_{k=${first}}^{${last}}`, `suma para k de ${first} a ${last}`));
      }
      if (definition.editor === 'limite') {
        const point = values.punto ? numericTex(values.punto) ?? 'a' : 'a';
        const side = values.lado === '-' ? '-' : '+';
        operator.replaceChildren(formula(`\\lim_{x\\to ${point}^{${side}}}`, `límite de x hacia ${point} por ${side}`));
      }
    },
    raw: () => math.hidden ? text.value : {latex:math.value},
    value() {
      if (math.hidden) return explicitProducts(text.value, false, variables);
      try {
        return expression(math.value, variables);
      } catch (error) {
        math.focus();
        if (math.value.includes('\\placeholder')) {
          math.position = 0;
          math.executeCommand('moveToNextPlaceholder');
        }
        throw error;
      }
    },
  };
}
