import { Pattern, PatternOp } from '../core/pattern';
import { Projectile } from '../core/projectile';
import { Tickable } from '../core/tick';
import { Simulator } from '../sim/simulator';
import { ProjectileRuntime } from '../sim/projectileRuntime';
import { evaluate, Context } from '../expr/evaluator';

export interface CompiledPatternOp {
  execute(sim: Simulator, state: PatternState, runtime: PatternRuntime): boolean | 'JUMP';
}

export class PatternState {
  public vars: Context = {};
  public opIndex: number = 0;
  public waitTicks: number = 0;
  public loops: number[] = [];

  constructor(initialParams: Context = {}) {
    this.vars = { ...initialParams };
  }
}

export class PatternRuntime implements Tickable {
  public state: PatternState;

  constructor(
    public patternDef: Pattern,
    public compiledOps: CompiledPatternOp[],
    public library: { projectiles: Record<string, Projectile>, patterns: Record<string, Pattern> },
    params: Context = {}
  ) {
    this.state = new PatternState(params);
    this.state.vars = { ...this.patternDef.params, ...params };
  }

  public tick(sim: Simulator): boolean {
    if (this.state.waitTicks > 0) {
      this.state.waitTicks--;
      return false;
    }

    while (this.state.opIndex < this.compiledOps.length) {
      const op = this.compiledOps[this.state.opIndex];
      const result = op.execute(sim, this.state, this);

      if (result === true) {
          // Op yielded (Wait)
          return false;
      } else if (result === false) {
          this.state.opIndex++;
      } else if (result === 'JUMP') {
          // opIndex was modified by the op
      }
    }

    return true; // Finished
  }
}

function compileOp(op: PatternOp, ops: CompiledPatternOp[], library: any) {
  switch (op.type) {
    case 'Wait':
      ops.push({
        execute(sim, state) {
          state.waitTicks = evaluate(op.ticks, { ...sim.getContext(), ...state.vars });
          state.opIndex++;
          return state.waitTicks > 0;
        }
      });
      break;
    case 'Fire':
      ops.push({
        execute(sim, state) {
          const angle = evaluate(op.angle as string | number, { ...sim.getContext(), ...state.vars });
          const speed = evaluate(op.speed as string | number, { ...sim.getContext(), ...state.vars });
          const pDef = library.projectiles[op.projectile];
          if (pDef) {
             sim.spawnProjectile(new ProjectileRuntime(sim.boss.x, sim.boss.y, angle, speed, pDef));
          }
          return false;
        }
      });
      break;
    case 'FireRing':
      ops.push({
        execute(sim, state) {
          const count = evaluate(op.count, { ...sim.getContext(), ...state.vars });
          const speed = evaluate(op.speed as string | number, { ...sim.getContext(), ...state.vars });
          const pDef = library.projectiles[op.projectile];
          if (pDef && count > 0) {
              const step = 360 / count;
              for (let i = 0; i < count; i++) {
                  sim.spawnProjectile(new ProjectileRuntime(sim.boss.x, sim.boss.y, i * step, speed, pDef));
              }
          }
          return false;
        }
      });
      break;
    case 'FireArc':
      ops.push({
        execute(sim, state) {
          const count = evaluate(op.count, { ...sim.getContext(), ...state.vars });
          const speed = evaluate(op.speed as string | number, { ...sim.getContext(), ...state.vars });
          const spread = evaluate(op.spread, { ...sim.getContext(), ...state.vars });
          const direction = evaluate(op.direction, { ...sim.getContext(), ...state.vars });

          const pDef = library.projectiles[op.projectile];
          if (pDef && count > 0) {
              if (count === 1) {
                  sim.spawnProjectile(new ProjectileRuntime(sim.boss.x, sim.boss.y, direction, speed, pDef));
              } else {
                  const startAngle = direction - spread / 2;
                  const step = spread / (count - 1);
                  for (let i = 0; i < count; i++) {
                      sim.spawnProjectile(new ProjectileRuntime(sim.boss.x, sim.boss.y, startAngle + i * step, speed, pDef));
                  }
              }
          }
          return false;
        }
      });
      break;
    case 'Set':
      ops.push({
        execute(sim, state) {
          state.vars[op.param] = evaluate(op.value, { ...sim.getContext(), ...state.vars });
          return false;
        }
      });
      break;
    case 'SpawnSubpattern':
      ops.push({
        execute(sim, state, runtime) {
           const subPatternDef = runtime.library.patterns[op.patternId];
           if (subPatternDef) {
               const compiledOps = compilePattern(subPatternDef, runtime.library);
               const subRuntime = new PatternRuntime(subPatternDef, compiledOps, runtime.library, state.vars);
               sim.activePatterns.push(subRuntime);
           }
           return false;
        }
      });
      break;
    case 'Loop': {
      // Loop begin
      const loopId = Math.random().toString();
      const loopBeginIndex = ops.length;
      ops.push({
         execute(sim, state) {
             const count = evaluate(op.count, { ...sim.getContext(), ...state.vars });
             if (state.vars[`_lmax_${loopId}`] === undefined) {
                 state.vars[`_lmax_${loopId}`] = count;
                 state.vars[`_lcur_${loopId}`] = 0;
                 state.vars['i'] = 0;
             }
             if (state.vars[`_lcur_${loopId}`] >= state.vars[`_lmax_${loopId}`]) {
                 // Clean up loop vars
                 delete state.vars[`_lmax_${loopId}`];
                 delete state.vars[`_lcur_${loopId}`];
                 // Jump to end of loop
                 state.opIndex = state.vars[`_lend_${loopId}`];
                 return 'JUMP';
             }
             return false;
         }
      });

      for (const childOp of op.ops) {
          compileOp(childOp, ops, library);
      }

      // Loop end
      const loopEndIndex = ops.length;
      // Patch the begin block so it knows where to jump
      ops.push({
          execute(sim, state) {
              state.vars[`_lend_${loopId}`] = loopEndIndex + 1; // Used by begin to jump out
              state.vars[`_lcur_${loopId}`]++;
              state.vars['i'] = state.vars[`_lcur_${loopId}`];
              state.opIndex = loopBeginIndex; // Jump back to condition check
              return 'JUMP';
          }
      });
      break;
    }
  }
}

export function compilePattern(
  pattern: Pattern,
  library: { projectiles: Record<string, Projectile>, patterns: Record<string, Pattern> }
): CompiledPatternOp[] {
  const ops: CompiledPatternOp[] = [];
  for (const op of pattern.ops) {
      compileOp(op, ops, library);
  }
  return ops;
}
