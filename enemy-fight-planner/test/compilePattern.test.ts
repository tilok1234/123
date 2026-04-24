import { expect, test } from 'vitest';
import { Pattern } from '../src/core/pattern';
import { Projectile } from '../src/core/projectile';
import { compilePattern, PatternRuntime } from '../src/compiler/compilePattern';
import { Simulator } from '../src/sim/simulator';

test('compiles and executes Wait', () => {
  const p: Pattern = {
    id: 'p1',
    ops: [{ type: 'Wait', ticks: 10 }]
  };
  const sim = new Simulator();
  const compiled = compilePattern(p, { projectiles: {}, patterns: {} });
  const runtime = new PatternRuntime(p, compiled, { projectiles: {}, patterns: {} });

  expect(runtime.tick(sim)).toBe(false); // Wait initiated
  expect(runtime.state.waitTicks).toBe(10);

  // Tick again should decrement
  expect(runtime.tick(sim)).toBe(false);
  expect(runtime.state.waitTicks).toBe(9);
});

test('compiles and executes Fire', () => {
  const proj: Projectile = { id: 'b1', sprite: 's1', hitboxRadius: 5 };
  const p: Pattern = {
    id: 'p1',
    ops: [{ type: 'Fire', projectile: 'b1', angle: 90, speed: 5 }]
  };
  const sim = new Simulator();
  const compiled = compilePattern(p, { projectiles: { b1: proj }, patterns: {} });
  const runtime = new PatternRuntime(p, compiled, { projectiles: { b1: proj }, patterns: {} });

  expect(runtime.tick(sim)).toBe(true); // Done immediately after firing
  expect(sim.projectiles.length).toBe(1);
  expect(sim.projectiles[0].speed).toBe(5);
});

test('compiles and executes Loop', () => {
    const proj: Projectile = { id: 'b1', sprite: 's1', hitboxRadius: 5 };
    const p: Pattern = {
      id: 'p1',
      ops: [
          {
              type: 'Loop',
              count: 3,
              ops: [
                  { type: 'Fire', projectile: 'b1', angle: 'i * 10', speed: 5 },
                  { type: 'Wait', ticks: 1 }
              ]
          }
      ]
    };
    const sim = new Simulator();
    const compiled = compilePattern(p, { projectiles: { b1: proj }, patterns: {} });
    const runtime = new PatternRuntime(p, compiled, { projectiles: { b1: proj }, patterns: {} });

    // Tick 1: init loop, fire (i=0) + set wait = 1
    expect(runtime.tick(sim)).toBe(false);
    expect(sim.projectiles.length).toBe(1);
    expect(sim.projectiles[0].angle).toBeCloseTo(0);

    // Tick 2: wait decrements to 0
    expect(runtime.tick(sim)).toBe(false);

    // Tick 3: jump back, fire (i=1) + set wait = 1
    expect(runtime.tick(sim)).toBe(false);
    expect(sim.projectiles.length).toBe(2);
    expect(sim.projectiles[1].angle).toBeCloseTo(10 * (Math.PI / 180));
});
