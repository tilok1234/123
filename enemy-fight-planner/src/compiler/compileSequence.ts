import { Sequence, SequenceOp } from '../core/sequence';
import { Pattern } from '../core/pattern';
import { Projectile } from '../core/projectile';
import { Tickable } from '../core/tick';
import { Simulator } from '../sim/simulator';
import { evaluate, Context } from '../expr/evaluator';
import { compilePattern, PatternRuntime } from './compilePattern';

export interface CompiledSequenceOp {
  execute(sim: Simulator, state: SequenceState, runtime: SequenceRuntime): boolean | 'JUMP';
}

export class SequenceState {
  public vars: Context = {};
  public opIndex: number = 0;
  public waitTicks: number = 0;
  public patternSlots: Record<string, PatternRuntime> = {};
  public pathDuration: number = 0;

  constructor() {}
}

export class SequenceRuntime implements Tickable {
  public state: SequenceState = new SequenceState();

  constructor(
    public sequenceDef: Sequence,
    public compiledOps: CompiledSequenceOp[],
    public library: { projectiles: Record<string, Projectile>, patterns: Record<string, Pattern> }
  ) {}

  public tick(sim: Simulator): boolean {
    if (this.state.waitTicks > 0) {
      this.state.waitTicks--;
      return false;
    }

    if (this.state.pathDuration > 0) {
      this.state.pathDuration--;
      // Basic movement simulation for v1
      sim.boss.y += 1;
      return false;
    }

    while (this.state.opIndex < this.compiledOps.length) {
      const op = this.compiledOps[this.state.opIndex];
      const result = op.execute(sim, this.state, this);

      if (result === true) {
          return false; // yielded
      } else if (result === false) {
          this.state.opIndex++;
      } else if (result === 'JUMP') {
          // Op updated opIndex
      }
    }

    return true; // Done
  }
}

function compileSequenceOp(op: SequenceOp, ops: CompiledSequenceOp[], library: any) {
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
    case 'StartPattern':
      ops.push({
        execute(sim, state, runtime) {
          const patternDef = library.patterns[op.patternId];
          if (patternDef) {
              const cOps = compilePattern(patternDef, library);
              const pRuntime = new PatternRuntime(patternDef, cOps, library);
              state.patternSlots[op.slot || 'default'] = pRuntime;
              sim.activePatterns.push(pRuntime);
          }
          return false;
        }
      });
      break;
    case 'StopPattern':
      ops.push({
        execute(sim, state) {
          const slot = op.slot || 'default';
          const pRuntime = state.patternSlots[slot];
          if (pRuntime) {
              sim.activePatterns = sim.activePatterns.filter(p => p !== pRuntime);
              delete state.patternSlots[slot];
          }
          return false;
        }
      });
      break;
    case 'MoveToPath':
      ops.push({
        execute(sim, state) {
          state.pathDuration = evaluate(op.duration, { ...sim.getContext(), ...state.vars });
          state.opIndex++;
          return state.pathDuration > 0;
        }
      });
      break;
    case 'ClearBullets':
      ops.push({
        execute(sim, state) {
          const radius = op.radius ? evaluate(op.radius, { ...sim.getContext(), ...state.vars }) : 9999;
          sim.clearBullets(radius, !!op.convertToDrop);
          return false;
        }
      });
      break;
    case 'SetParam':
      ops.push({
        execute(sim, state) {
          const slot = op.slot || 'default';
          const pRuntime = state.patternSlots[slot];
          if (pRuntime) {
              pRuntime.state.vars[op.param] = evaluate(op.value, { ...sim.getContext(), ...state.vars });
          }
          return false;
        }
      });
      break;
    case 'PhaseTransition': {
      // Create a polling loop that blocks sequence execution until HP drops
      const blockIndex = ops.length;
      ops.push({
        execute(sim, state) {
          const hpPercent = sim.boss.hp / sim.boss.maxHp;
          if (hpPercent <= op.hpPercent) {
             sim.boss.phase++;
             return false; // Proceed to phase ops
          }
          // Block and yield
          return true;
        }
      });
      // Flatten inner ops
      for (const childOp of op.ops) {
         compileSequenceOp(childOp, ops, library);
      }
      break;
    }
    case 'SpawnDrop':
      ops.push({
        execute(sim, state) {
           // Not fully simulated for v1 beyond acknowledging event
           return false;
        }
      });
      break;
  }
}

export function compileSequence(sequence: Sequence, library: any): CompiledSequenceOp[] {
   const ops: CompiledSequenceOp[] = [];
   for (const op of sequence.ops) {
       compileSequenceOp(op, ops, library);
   }
   return ops;
}
