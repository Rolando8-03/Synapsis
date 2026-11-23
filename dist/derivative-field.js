import { MathfieldElement, convertAsciiMathToLatex, convertLatexToAsciiMath } from './vendor/mathlive/mathlive.min.mjs';
import { node } from './matrix-input.js';

MathfieldElement.fontsDirectory = new URL('./vendor/katex/fonts/', import.meta.url).href;
MathfieldElement.soundsDirectory = null;
MathfieldElement.locale = 'es';

function expression(latex) {
  // La conversión ASCII puede omitir un exponente vacío o un símbolo no admitido.
  const symbols = latex.replace(/\\(?:m?left|m?right|cdot|times|div|sin|cos|tan|ln|log|exp|pi)\b/g, '');
  if (/[^a-zA-Z0-9\s.+*^()/{}-]|\{\s*\}/u.test(symbols)) {
    throw new Error('Completá la potencia o usá la entrada de texto para esta expresión.');
  }
  return convertLatexToAsciiMath(latex).trim();
}

function visualLatex(text) {
  const normalize = s => s.replace(/\s+/g, '').replaceAll('**', '^');
  try {
    const latex = convertAsciiMathToLatex(text.replaceAll('**', '^'));
    if (normalize(expression(latex)) === normalize(text)) return latex;
  } catch { /* Conservá la entrada original si no hay conversión fiel. */ }
  return null;
}

export function derivativeField(definition, initial, onChange) {
  const element = node('div', 'ws-field ws-full-field ws-derivative');
  const label = node('label', '', definition.label);
  const math = new MathfieldElement();
  math.id = 'ws-derivative-math';
  math.setAttribute('aria-label', definition.label);
  math.mathVirtualKeyboardPolicy = 'manual';
  math.smartSuperscript = false;

  const text = node('input');
  text.id = 'ws-derivative-text';
  text.type = 'text';
  text.maxLength = 500;
  text.autocomplete = 'off';
  text.spellcheck = false;

  const keys = node('div', 'ws-power-keys');
  keys.setAttribute('role', 'group');
  keys.setAttribute('aria-label', 'Teclado de potencias');
  for (const [caption, command, name] of [
    ['x', ['insert', 'x']], ['□ⁿ', 'moveToSuperscript', 'Exponente'],
    ...Array.from('1234567890', digit => [digit, ['insert', digit]]),
    ['−', ['insert', '-']], ['→', 'moveToNextChar', 'Avanzar'], ['⌫', 'deleteBackward', 'Borrar'],
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
  element.append(label, math, text, keys, toggle, feedback);

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

  toggle.addEventListener('click', () => {
    if (math.hidden) {
      const latex = visualLatex(text.value);
      if (latex === null) {
        feedback.textContent = 'Esta expresión se edita como texto. Para empezar una potencia nueva, vaciá el campo.';
        feedback.hidden = false;
        return;
      }
      math.setValue(latex, {silenceNotifications:true});
      useVisual(true);
      math.focus();
    } else {
      try { text.value = expression(math.value); }
      catch { text.value = math.value; }
      useVisual(false);
      text.focus();
    }
    onChange();
  });
  element.addEventListener('input', onChange);
  set(initial);
  return {
    definition, element, set,
    raw: () => math.hidden ? text.value : {latex:math.value},
    value: () => math.hidden ? text.value.trim() : expression(math.value),
  };
}
