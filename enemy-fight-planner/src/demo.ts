import { Simulator } from './sim/simulator';
import { compileSequence, SequenceRuntime } from './compiler/compileSequence';
import { hashSimState } from './sim/hashing';
import * as fs from 'fs';
import * as path from 'path';

function loadJson(relativePath: string) {
    // Navigate from dist back to src
    return JSON.parse(fs.readFileSync(path.join(__dirname, '../src', relativePath), 'utf-8'));
}

async function runDemo() {
    console.log('--- Enemy Fight Planner Demo ---');
    console.log('Loading library...');

    const library = {
        patterns: {
            basic_ring: loadJson('./samples/patterns/basic_ring.json'),
            aimed_fan: loadJson('./samples/patterns/aimed_fan.json'),
            double_spiral: loadJson('./samples/patterns/double_spiral.json'),
            sweeping_arc: loadJson('./samples/patterns/sweeping_arc.json'),
            phase_flower: loadJson('./samples/patterns/phase_flower.json'),
        },
        projectiles: {
            bullet_round: { id: 'bullet_round', sprite: 'round.png', hitboxRadius: 5 },
            bullet_knife: { id: 'bullet_knife', sprite: 'knife.png', hitboxRadius: 3 },
            bullet_large: { id: 'bullet_large', sprite: 'large.png', hitboxRadius: 10 },
        }
    };

    const bossSequence = loadJson('./samples/sequences/boss.forest_keeper.json');

    console.log('Initializing Simulator...');
    const sim = new Simulator(12345);
    sim.sequenceRuntime = new SequenceRuntime(
        bossSequence,
        compileSequence(bossSequence, library),
        library
    );

    console.log('Running 300 ticks (5 seconds at 60Hz)...');
    for (let i = 0; i < 300; i++) {
        sim.tick();
        if (i % 60 === 0 && i > 0) {
            console.log(`[Tick ${i}] Active Projectiles: ${sim.projectiles.length}`);
        }
    }

    console.log(`[Tick 300] Final Active Projectiles: ${sim.projectiles.length}`);
    console.log(`Final Sim State Hash: ${hashSimState(sim).slice(0, 16)}...`);
    console.log('Demo finished.');
}

runDemo().catch(console.error);
