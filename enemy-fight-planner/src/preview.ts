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
} as any;

const canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const lblTick = document.getElementById('lblTick')!;
const btnPlayPause = document.getElementById('btnPlayPause')!;
const btnRestart = document.getElementById('btnRestart')!;

let sim: Simulator;
let isPaused = false;
let animationId: number;

const keys = {
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false,
    w: false,
    a: false,
    s: false,
    d: false,
};

window.addEventListener('keydown', (e) => {
    if (keys.hasOwnProperty(e.key)) {
        (keys as any)[e.key] = true;
    }
});

window.addEventListener('keyup', (e) => {
    if (keys.hasOwnProperty(e.key)) {
        (keys as any)[e.key] = false;
    }
});

function initSim() {
    sim = new Simulator(12345);
    sim.sequenceRuntime = new SequenceRuntime(
        bossSequence as any,
        compileSequence(bossSequence as any, library),
        library
    );
    sim.boss.x = 0;
    sim.boss.y = -200;
}

function processInput() {
    let vx = 0;
    let vy = 0;
    const speed = sim.player.speed;

    if (keys.ArrowUp || keys.w) vy -= speed;
    if (keys.ArrowDown || keys.s) vy += speed;
    if (keys.ArrowLeft || keys.a) vx -= speed;
    if (keys.ArrowRight || keys.d) vx += speed;

    // Normalize diagonal speed
    if (vx !== 0 && vy !== 0) {
        const length = Math.sqrt(vx * vx + vy * vy);
        vx = (vx / length) * speed;
        vy = (vy / length) * speed;
    }

    sim.player.vx = vx;
    sim.player.vy = vy;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);

    // Draw Boss
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(sim.boss.x, sim.boss.y, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.stroke();

    // Draw Boss HP Bar
    const hpPercent = sim.boss.hp / sim.boss.maxHp;
    ctx.fillStyle = 'darkred';
    ctx.fillRect(sim.boss.x - 30, sim.boss.y - 45, 60, 5);
    ctx.fillStyle = 'lime';
    ctx.fillRect(sim.boss.x - 30, sim.boss.y - 45, 60 * hpPercent, 5);

    // Draw Player
    ctx.fillStyle = 'blue';
    ctx.beginPath();
    ctx.moveTo(sim.player.x, sim.player.y - 15);
    ctx.lineTo(sim.player.x - 10, sim.player.y + 10);
    ctx.lineTo(sim.player.x + 10, sim.player.y + 10);
    ctx.closePath();
    ctx.fill();

    // Draw Player Hitbox
    ctx.fillStyle = 'cyan';
    ctx.beginPath();
    ctx.arc(sim.player.x, sim.player.y, sim.player.hitboxRadius, 0, Math.PI * 2);
    ctx.fill();

    // Draw Player HP Bar
    const playerHpPercent = sim.player.hp / sim.player.maxHp;
    ctx.fillStyle = 'darkred';
    ctx.fillRect(sim.player.x - 20, sim.player.y + 20, 40, 4);
    ctx.fillStyle = 'cyan';
    ctx.fillRect(sim.player.x - 20, sim.player.y + 20, 40 * playerHpPercent, 4);

    // Draw Player Projectiles
    ctx.fillStyle = 'yellow';
    for (const p of sim.playerProjectiles) {
        if (!p.active) continue;
        ctx.fillRect(p.x - 2, p.y - 8, 4, 16);
    }

    // Draw Boss Projectiles
    for (const p of sim.projectiles) {
        if (!p.active) continue;

        let color = 'yellow';
        let radius = p.hitboxRadius;

        if (p.id === 'bullet_large') {
            color = 'orange';
        } else if (p.id === 'bullet_knife') {
            color = 'magenta';
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
        processInput();
        sim.tick();
        lblTick.textContent = `Tick: ${sim.tickCount} | Boss Phase: ${sim.boss.phase} | Boss HP: ${sim.boss.hp}`;
    }
    draw();
    animationId = requestAnimationFrame(update);
}

btnPlayPause.addEventListener('click', () => {
    isPaused = !isPaused;
    btnPlayPause.textContent = isPaused ? 'Play' : 'Pause';
    // Remove focus so spacebar doesn't re-trigger button while dodging
    btnPlayPause.blur();
});

btnRestart.addEventListener('click', () => {
    cancelAnimationFrame(animationId);
    initSim();
    isPaused = false;
    btnPlayPause.textContent = 'Pause';
    btnRestart.blur();
    update();
});

// Start
initSim();
update();
