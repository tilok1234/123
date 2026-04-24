import { Tickable } from '../core/tick';
import { Simulator } from './simulator';
import { Sequence, SequenceOp } from '../core/sequence';

// We'll flesh this out fully in the compiler step
export class SequenceRuntime implements Tickable {
  constructor(public id: string, private ops: any[]) {}
  tick(sim: Simulator): boolean { return true; }
}
