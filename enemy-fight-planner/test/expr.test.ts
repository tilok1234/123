import { expect, test } from 'vitest';
import { evaluate } from '../src/expr/evaluator';

test('evaluates simple math', () => {
  expect(evaluate('1 + 2 * 3', {})).toBe(7);
  expect(evaluate('(1 + 2) * 3', {})).toBe(9);
});

test('evaluates variables', () => {
  expect(evaluate('180 + i * step', { i: 2, step: 15 })).toBe(210);
});

test('evaluates functions', () => {
  expect(evaluate('min(10, 5)', {})).toBe(5);
  expect(evaluate('lerp(140, 220, rank)', { rank: 0.5 })).toBe(180);
});

test('evaluates logic and ternary', () => {
  expect(evaluate('hpPercent <= 0.70 ? 24 : 12', { hpPercent: 0.5 })).toBe(24);
  expect(evaluate('hpPercent <= 0.70 ? 24 : 12', { hpPercent: 0.9 })).toBe(12);
  expect(evaluate('!0', {})).toBe(1);
  expect(evaluate('1 && 0', {})).toBe(0);
});

test('evaluates nested expressions', () => {
  expect(evaluate('sin(deg2rad(i * 15)) * 30', { i: 2 })).toBeCloseTo(15);
});
