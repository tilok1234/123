import { expect, test } from 'vitest';
import { Sequence } from '../src/core/sequence';
import { Pattern } from '../src/core/pattern';
import { Projectile } from '../src/core/projectile';
import { compileSequence, SequenceRuntime } from '../src/compiler/compileSequence';
import { Simulator } from '../src/sim/simulator';

test('compiles and executes Wait', () => {
  const seq: Sequence = {
    id: 's1',
    ops: [{ type: 'Wait', ticks: 10 }]
  };
  const sim = new Simulator();
  const compiled = compileSequence(seq, { projectiles: {}, patterns: {} });
  const runtime = new SequenceRuntime(seq, compiled, { projectiles: {}, patterns: {} });

  expect(runtime.tick(sim)).toBe(false);
  expect(runtime.state.waitTicks).toBe(10);
});

test('starts and stops pattern', () => {
  const p: Pattern = {
    id: 'p1',
    ops: [{ type: 'Wait', ticks: 999 }]
  };
  const seq: Sequence = {
    id: 's1',
    ops: [
      { type: 'StartPattern', patternId: 'p1', slot: 'main' },
      { type: 'Wait', ticks: 1 },
      { type: 'StopPattern', slot: 'main' }
    ]
  };
  const sim = new Simulator();
  const compiled = compileSequence(seq, { projectiles: {}, patterns: { p1: p } });
  const runtime = new SequenceRuntime(seq, compiled, { projectiles: {}, patterns: { p1: p } });

  // Tick 1: Starts pattern, hits Wait(1) (wait = 1)
  expect(runtime.tick(sim)).toBe(false);
  expect(sim.activePatterns.length).toBe(1);

  // Tick 2: finishes Wait(1) (wait = 0)
  expect(runtime.tick(sim)).toBe(false);

  // Tick 3: executes StopPattern, finishes sequence
  expect(runtime.tick(sim)).toBe(true);
  expect(sim.activePatterns.length).toBe(0);
});
