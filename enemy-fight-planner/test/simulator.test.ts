import { expect, test } from 'vitest';
import { Simulator } from '../src/sim/simulator';
import { ProjectileRuntime } from '../src/sim/projectileRuntime';

test('simulator core loop runs deterministically', () => {
  const sim1 = new Simulator(42);
  const sim2 = new Simulator(42);

  expect(sim1.rng.next()).toBe(sim2.rng.next());

  const p1 = new ProjectileRuntime(0, 0, 90, 5, { id: 'p1', sprite: 's1', hitboxRadius: 5 });
  const p2 = new ProjectileRuntime(0, 0, 90, 5, { id: 'p1', sprite: 's1', hitboxRadius: 5 });

  sim1.spawnProjectile(p1);
  sim2.spawnProjectile(p2);

  sim1.tick();
  sim2.tick();

  expect(sim1.projectiles[0].x).toBeCloseTo(0);
  expect(sim1.projectiles[0].y).toBeCloseTo(5);
  expect(sim1.projectiles[0].x).toBe(sim2.projectiles[0].x);
  expect(sim1.projectiles[0].y).toBe(sim2.projectiles[0].y);
});
