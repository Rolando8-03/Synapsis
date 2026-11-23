import assert from 'node:assert/strict';
import test from 'node:test';
import { explicitProducts } from '../dist/expression-input.mjs';

test('agrupa factores conservando paréntesis, exponente, signo y llamadas', () => {
  for (const [input, expected] of [
    ['-2(x-1)', '-2*(x-1)'], ['(x-1)(x+1)', '(x-1)*(x+1)'],
    ['-2x^2', '-2*x^2'], ['2 sin (3x)', '2*sin(3*x)'],
    ['((1)/(2x))', '((1)/(2*x))'], ['1e-3*x**2', '1e-3*x**2'],
    ['π × x ÷ 2', 'pi*x/2'], ['−sqrt(x)', '-sqrt(x)'],
  ]) assert.equal(explicitProducts(input), expected);
});

test('localiza símbolos, cocientes y argumentos ambiguos', () => {
  assert.throws(() => explicitProducts('2x+y'), /«y»/);
  assert.throws(() => explicitProducts('1/2x'), /denominador/);
  assert.throws(() => explicitProducts('sin x'), /argumento de sin/);
  assert.throws(() => explicitProducts('2e-3', true), /potencia de 10/);
});
