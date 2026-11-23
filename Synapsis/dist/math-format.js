import { node } from './matrix-input.js';

export function numericTex(value) {
  const text = String(value);
  const fraction = /^(-?)(\d+)\/(\d+)$/.exec(text);
  if (fraction) return `${fraction[1]}\\frac{${fraction[2]}}{${fraction[3]}}`;
  const power = /^([+-]?(?:\d+(?:\.\d+)?))e([+-]?\d+)$/i.exec(text);
  if (power) return `${power[1]}\\times10^{${power[2]}}`;
  return /^[+-]?\d+(?:\.\d+)?$/.test(text) ? text : null;
}

export function math(tex, fallback = tex, display = false) {
  const element = node(display ? 'div' : 'span', display ? 'ws-math ws-math-display' : 'ws-math');
  element.dataset.plain = fallback;
  if (window.katex) window.katex.render(tex, element, {
    displayMode: display, output: 'htmlAndMathml', trust: false, throwOnError: false,
  });
  else element.textContent = fallback;
  return element;
}

export function matrixFormula(rows, caption, independent = false) {
  if (!rows.length || !rows[0]?.length || rows.length > 7 || rows[0].length > 8) return null;
  const entries = rows.map(row => row.map(numericTex));
  if (entries.some(row => row.some(value => value === null))) return null;
  const body = entries.map(row => row.join('&')).join('\\\\');
  const columns = 'r'.repeat(entries[0].length - 1) + '|r';
  const tex = independent
    ? `\\left[\\begin{array}{${columns}}${body}\\end{array}\\right]`
    : `\\begin{bmatrix}${body}\\end{bmatrix}`;
  const wrap = node('div', 'ws-matrix-formula');
  if (caption) wrap.append(node('p','ws-muted',caption));
  wrap.append(math(tex, rows.map(row => row.join('\t')).join('\n'), true));
  return wrap;
}
