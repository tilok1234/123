import { expect, test } from 'vitest';
import { Simulator } from '../src/sim/simulator';
import { hashSimState } from '../src/sim/hashing';
import { compileSequence, SequenceRuntime } from '../src/compiler/compileSequence';
import * as fs from 'fs';
import * as path from 'path';

test('replays deterministic sequence to fixed tick', () => {
    const seqJson = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/samples/sequences/boss.forest_keeper.json'), 'utf-8'));
    const doubleSpiralJson = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/samples/patterns/double_spiral.json'), 'utf-8'));
    const pdef = { id: 'bullet_round', sprite: 's1', hitboxRadius: 5 };

    const library = {
        patterns: { double_spiral: doubleSpiralJson },
        projectiles: { bullet_round: pdef }
    };

    const sim1 = new Simulator(12345);
    sim1.sequenceRuntime = new SequenceRuntime(seqJson, compileSequence(seqJson, library), library);

    const sim2 = new Simulator(12345);
    sim2.sequenceRuntime = new SequenceRuntime(seqJson, compileSequence(seqJson, library), library);

    for (let i = 0; i < 150; i++) {
        sim1.tick();
        sim2.tick();
    }

    expect(hashSimState(sim1)).toEqual(hashSimState(sim2));
    expect(sim1.tickCount).toBe(150);
});
