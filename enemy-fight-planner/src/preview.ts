import { Simulator } from './sim/simulator';
import { compileSequence, SequenceRuntime } from './compiler/compileSequence';
import basic_ring from './samples/patterns/basic_ring.json';
import aimed_fan from './samples/patterns/aimed_fan.json';
import double_spiral from './samples/patterns/double_spiral.json';
import sweeping_arc from './samples/patterns/sweeping_arc.json';
import phase_flower from './samples/patterns/phase_flower.json';
import bossSequence from './samples/sequences/boss.forest_keeper.json';

const library = {
    patterns: {
        basic_ring,
        aimed_fan,
        double_spiral,
        sweeping_arc,
        phase_flower,
    },
    projectiles: {
        bullet_round: { id: 'bullet_round', sprite: 'round.png', hitboxRadius: 5 },
        bullet_knife: { id: 'bullet_knife', sprite: 'knife.png', hitboxRadius: 3 },
        bullet_large: { id: 'bullet_large', sprite: 'large.png', hitboxRadius: 10 },
    }
} as any; // Cast to any to bypass strict type checking for the JSON imports for now

const canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const lblTick = document.getElementById('lblTick')!;
const btnPlayPause = document.getElementById('btnPlayPause')!;
const btnRestart = document.getElementById('btnRestart')!;

let sim: Simulator;
let isPaused = false;
let animationId: number;

function initSim() {
    sim = new Simulator(12345);
    sim.sequenceRuntime = new SequenceRuntime(
        bossSequence as any,
        compileSequence(bossSequence as any, library),
        library
    );
    // Center boss visually initially
    sim.boss.x = 0;
    sim.boss.y = -200;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Save context and translate so 0,0 is center of screen
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);

    // Draw Boss
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(sim.boss.x, sim.boss.y, 20, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.stroke();

    // Draw Boss HP Bar
    const hpPercent = sim.boss.hp / sim.boss.maxHp;
    ctx.fillStyle = 'darkred';
    ctx.fillRect(sim.boss.x - 30, sim.boss.y - 35, 60, 5);
    ctx.fillStyle = 'lime';
    ctx.fillRect(sim.boss.x - 30, sim.boss.y - 35, 60 * hpPercent, 5);

    // Draw Projectiles
    for (const p of sim.projectiles) {
        if (!p.active) continue;

        let color = 'yellow';
        let radius = p.hitboxRadius;

        if (p.id === 'bullet_large') {
            color = 'orange';
        } else if (p.id === 'bullet_knife') {
            color = 'cyan';
            radius = 4;
        }

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
    }

    ctx.restore();
}

function update() {
    if (!isPaused) {
        sim.tick();
        // Automatically decrease HP over time to trigger phase transitions
        if (sim.tickCount > 120 && sim.boss.hp > 0 && sim.tickCount % 2 === 0) {
            sim.boss.hp -= 2; // Simulate DPS
            if (sim.boss.hp < 0) sim.boss.hp = 0;
        }
        lblTick.textContent = `Tick: ${sim.tickCount} | Phase: ${sim.boss.phase}`;
    }
    draw();
    animationId = requestAnimationFrame(update);
}

btnPlayPause.addEventListener('click', () => {
    isPaused = !isPaused;
    btnPlayPause.textContent = isPaused ? 'Play' : 'Pause';
});

btnRestart.addEventListener('click', () => {
    cancelAnimationFrame(animationId);
    initSim();
    isPaused = false;
    btnPlayPause.textContent = 'Pause';
    update();
});

// Start
initSim();
update();
