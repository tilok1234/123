import { Projectile, Movement } from '../core/types';
import { Simulator } from './simulator';

export class ProjectileRuntime {
  public x: number;
  public y: number;
  public vx: number;
  public vy: number;
  public angle: number;
  public speed: number;
  public id: string;
  public sprite: string;
  public hitboxRadius: number;
  public damage: number;
  public movement?: Movement;
  public active: boolean = true;
  public time: number = 0;

  constructor(
    x: number,
    y: number,
    angleDeg: number,
    speed: number,
    def: Projectile
  ) {
    this.x = x;
    this.y = y;
    this.angle = angleDeg * (Math.PI / 180);
    this.speed = speed;
    this.vx = Math.cos(this.angle) * this.speed;
    this.vy = Math.sin(this.angle) * this.speed;
    this.id = def.id;
    this.sprite = def.sprite;
    this.hitboxRadius = def.hitboxRadius;
    this.damage = def.damage ?? 1;
    this.movement = def.movement;
  }

  public tick(sim?: Simulator): void {
    if (!this.active) return;

    if (this.movement) {
      if (this.movement.type === 'Accelerating' && this.movement.acceleration) {
        this.speed += this.movement.acceleration;
        if (this.movement.maxSpeed !== undefined && this.speed > this.movement.maxSpeed) {
          this.speed = this.movement.maxSpeed;
        }
        this.vx = Math.cos(this.angle) * this.speed;
        this.vy = Math.sin(this.angle) * this.speed;
      } else if (this.movement.type === 'Homing' && this.movement.turnRate && sim) {
          // Calculate angle to player
          const targetAngle = Math.atan2(sim.player.y - this.y, sim.player.x - this.x);

          // Normalize angles for shortest turn
          let diff = targetAngle - this.angle;
          while (diff > Math.PI) diff -= Math.PI * 2;
          while (diff < -Math.PI) diff += Math.PI * 2;

          // Turn towards target
          const turnRateRad = this.movement.turnRate * (Math.PI / 180);
          if (Math.abs(diff) <= turnRateRad) {
              this.angle = targetAngle;
          } else {
              this.angle += Math.sign(diff) * turnRateRad;
          }

          this.vx = Math.cos(this.angle) * this.speed;
          this.vy = Math.sin(this.angle) * this.speed;
      }
    }

    this.x += this.vx;
    this.y += this.vy;
    this.time++;
  }
}
