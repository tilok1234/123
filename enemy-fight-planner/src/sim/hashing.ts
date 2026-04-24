import { Simulator } from './simulator';

export function hashSimState(sim: Simulator): string {
    const state = {
        tick: sim.tickCount,
        boss: sim.boss,
        projectiles: sim.projectiles.map(p => ({
            x: Math.round(p.x * 1000) / 1000,
            y: Math.round(p.y * 1000) / 1000,
            id: p.id
        }))
    };
    return JSON.stringify(state);
}
