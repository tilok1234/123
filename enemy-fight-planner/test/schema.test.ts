import { expect, test } from 'vitest';
import { validatePattern, validateSequence, getErrors } from '../src/validation/validate';

test('validates a correct pattern', () => {
  const pattern = {
    id: 'test_pattern',
    params: { speed: 5 },
    ops: [
      { type: 'Wait', ticks: 10 },
      { type: 'Fire', projectile: 'bullet1', angle: 90, speed: 'speed * 2' }
    ]
  };
  const isValid = validatePattern(pattern);
  expect(getErrors()).toBeNull();
  expect(isValid).toBe(true);
});

test('invalidates incorrect pattern', () => {
  const pattern = {
    id: 'test_pattern',
    ops: [
      { type: 'Fire' } // Missing required fields
    ]
  };
  const isValid = validatePattern(pattern);
  expect(isValid).toBe(false);
  expect(getErrors()?.length).toBeGreaterThan(0);
});

test('validates a correct sequence', () => {
  const sequence = {
    id: 'test_sequence',
    ops: [
      { type: 'StartPattern', patternId: 'pat1', slot: 'main' },
      { type: 'Wait', ticks: 60 }
    ]
  };
  const isValid = validateSequence(sequence);
  expect(getErrors()).toBeNull();
  expect(isValid).toBe(true);
});
