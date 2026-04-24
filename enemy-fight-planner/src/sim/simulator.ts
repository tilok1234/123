import { RNG } from './rng';
import { ProjectileRuntime } from './projectileRuntime';
import { Context } from '../expr/evaluator';

export interface BossState {
  x: number;
  y: number;
  hp: number;
  maxHp: number;
  phase: number;
}

export class Simulator {
  public rng: RNG;
  public tickCount: number = 0;
  public projectiles: ProjectileRuntime[] = [];
  public boss: BossState;

  // Active pattern runtimes (to be defined by compiler)
  public activePatterns: any[] = [];
  public sequenceRuntime: any = null;

  constructor(seed: number = 12345) {
    this.rng = new RNG(seed);
    this.boss = { x: 0, y: 0, hp: 1000, maxHp: 1000, phase: 1 };
  }

  public getContext(): Context {
    return {
      t: this.tickCount,
      time: this.tickCount,
      hp: this.boss.hp,
      hpPercent: this.boss.hp / this.boss.maxHp,
      phase: this.boss.phase,
      rank: 0.5, // Arbitrary rank for v1
      rand: this.rng.next(),
    };
  }

  public tick(): void {
    this.tickCount++;

    if (this.sequenceRuntime) {
      this.sequenceRuntime.tick(this);
    }

    for (const pattern of this.activePatterns) {
      pattern.tick(this);
    }

    // Tick projectiles
    for (const p of this.projectiles) {
      p.tick();
    }

    // Filter inactive projectiles or out of bounds
    this.projectiles = this.projectiles.filter((p) => {
       // Assuming bounds of -1000 to 1000 for simple culling
       return p.active && p.x > -1000 && p.x < 1000 && p.y > -1000 && p.y < 1000;
    });
  }

  public spawnProjectile(p: ProjectileRuntime) {
      this.projectiles.push(p);
  }

  public clearBullets(radius: number, convertToDrop: boolean) {
      // Simplistic clear around boss
      for(const p of this.projectiles) {
          const dx = p.x - this.boss.x;
          const dy = p.y - this.boss.y;
          if (Math.sqrt(dx*dx + dy*dy) <= radius) {
              p.active = false;
              // Ignore drop conversion for v1 sim logic
          }
      }
  }
}
