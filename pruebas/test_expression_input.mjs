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

test('lee operadores de cálculo sin partir el integrando ni los límites', async () => {
  const {calculusNotation} = await import('../dist/expression-input.mjs');
  assert.deepEqual(calculusNotation(String.raw`\int_{\frac{1}{2}}^{2} 2x\cos(x^{2})\,\mathrm{d}x`), {
    operacion:'integral', inferior:String.raw`\frac{1}{2}`, superior:'2', variable:'x',
    expresion:String.raw`2x\cos(x^{2})`,
  });
  assert.deepEqual(calculusNotation(String.raw`\lim_{x\to 1^{+}}x^2`), {
    operacion:'limite', variable:'x', punto:'1', lado:'+', expresion:'x^2',
  });
  assert.equal(calculusNotation(String.raw`\lim_{x\to -\infty}x`).lado, '-');
  assert.equal(calculusNotation(String.raw`\frac{d}{dx}x^2`).operacion, 'derivada');
  assert.throws(() => calculusNotation(String.raw`\int x^2`), /diferencial/);
});
