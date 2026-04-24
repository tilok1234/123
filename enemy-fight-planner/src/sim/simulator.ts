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

export interface PlayerState {
  x: number;
  y: number;
  vx: number;
  vy: number;
  hp: number;
  maxHp: number;
  hitboxRadius: number;
  speed: number;
  cooldown: number;
}

export class Simulator {
  public rng: RNG;
  public tickCount: number = 0;

  public projectiles: ProjectileRuntime[] = [];
  public playerProjectiles: ProjectileRuntime[] = [];

  public boss: BossState;
  public player: PlayerState;

  // Active pattern runtimes (to be defined by compiler)
  public activePatterns: any[] = [];
  public sequenceRuntime: any = null;

  constructor(seed: number = 12345) {
    this.rng = new RNG(seed);
    this.boss = { x: 0, y: 0, hp: 1000, maxHp: 1000, phase: 1 };
    this.player = { x: 0, y: 200, vx: 0, vy: 0, hp: 10, maxHp: 10, hitboxRadius: 4, speed: 5, cooldown: 0 };
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

    this.tickPlayer();

    // Tick projectiles (pass sim so homing works)
    for (const p of this.projectiles) {
      p.tick(this);
    }
    for (const p of this.playerProjectiles) {
      p.tick(this);
    }

    this.checkCollisions();

    // Filter inactive projectiles or out of bounds
    this.projectiles = this.projectiles.filter((p) => {
       return p.active && p.x > -1000 && p.x < 1000 && p.y > -1000 && p.y < 1000;
    });
    this.playerProjectiles = this.playerProjectiles.filter((p) => {
       return p.active && p.x > -1000 && p.x < 1000 && p.y > -1000 && p.y < 1000;
    });
  }

  private tickPlayer(): void {
     this.player.x += this.player.vx;
     this.player.y += this.player.vy;

     // Keep player in bounds (rough bounds for a vertical shmup)
     if (this.player.x < -380) this.player.x = -380;
     if (this.player.x > 380) this.player.x = 380;
     if (this.player.y < -280) this.player.y = -280;
     if (this.player.y > 280) this.player.y = 280;

     // Player Auto-fire logic
     if (this.player.cooldown > 0) {
         this.player.cooldown--;
     } else {
         // Fire two straight shots upwards
         const pDef = { id: 'player_shot', sprite: 'laser.png', hitboxRadius: 4, damage: 2 };
         this.playerProjectiles.push(new ProjectileRuntime(this.player.x - 10, this.player.y - 10, -90, 15, pDef));
         this.playerProjectiles.push(new ProjectileRuntime(this.player.x + 10, this.player.y - 10, -90, 15, pDef));
         this.player.cooldown = 4; // Fire rate
     }
  }

  private checkCollisions(): void {
     // Boss projectiles -> Player
     for (const p of this.projectiles) {
         if (!p.active) continue;
         const dx = p.x - this.player.x;
         const dy = p.y - this.player.y;
         const distSq = dx * dx + dy * dy;
         const radSum = p.hitboxRadius + this.player.hitboxRadius;

         if (distSq <= radSum * radSum) {
             p.active = false;
             this.player.hp -= (p.damage || 1);
             if (this.player.hp < 0) this.player.hp = 0;
         }
     }

     // Player projectiles -> Boss (assuming boss has a large static radius of 30)
     const bossRadiusSq = 30 * 30;
     for (const p of this.playerProjectiles) {
         if (!p.active) continue;
         const dx = p.x - this.boss.x;
         const dy = p.y - this.boss.y;
         const distSq = dx * dx + dy * dy;

         if (distSq <= bossRadiusSq) {
             p.active = false;
             this.boss.hp -= (p.damage || 1);
             if (this.boss.hp < 0) this.boss.hp = 0;
         }
     }
  }

  public spawnProjectile(p: ProjectileRuntime) {
      this.projectiles.push(p);
  }

  public clearBullets(radius: number, convertToDrop: boolean) {
      for(const p of this.projectiles) {
          const dx = p.x - this.boss.x;
          const dy = p.y - this.boss.y;
          if (Math.sqrt(dx*dx + dy*dy) <= radius) {
              p.active = false;
          }
      }
  }
}
