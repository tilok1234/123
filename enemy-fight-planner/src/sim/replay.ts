import { Simulator } from './simulator';
import { ProjectileRuntime } from './projectileRuntime';

export function runSimToTick(sim: Simulator, targetTick: number) {
  while (sim.tickCount < targetTick) {
    sim.tick();
  }
}
