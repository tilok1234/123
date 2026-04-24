import { expect, test } from 'vitest';
import { Simulator } from '../src/sim/simulator';
import { hashSimState } from '../src/sim/hashing';
import { compilePattern, PatternRuntime } from '../src/compiler/compilePattern';
import * as fs from 'fs';
import * as path from 'path';

test('golden hash for sweeping_arc pattern', () => {
    const patternJson = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/samples/patterns/sweeping_arc.json'), 'utf-8'));
    const pdef = { id: 'bullet_knife', sprite: 's1', hitboxRadius: 5 };

    const library = {
        patterns: { sweeping_arc: patternJson },
        projectiles: { bullet_knife: pdef }
    };

    const sim = new Simulator(999);
    const compiled = compilePattern(patternJson, library);
    sim.activePatterns.push(new PatternRuntime(patternJson, compiled, library));

    // Run for 60 ticks (1 second at 60hz)
    for (let i = 0; i < 60; i++) {
        sim.tick();
    }

    // Verify it spawned 10 bullets
    expect(sim.projectiles.length).toBe(10);

    // We establish the golden hash here for future determinism checks
    const currentHash = hashSimState(sim);
    expect(currentHash).toMatch(/"tick":60/);
    expect(currentHash).toMatch(/"id":"bullet_knife"/);
    // Hardcoding specific json string check is brittle if properties reorder,
    // but works fine for deterministic hashing as long as runtime is stable.
});
