export interface Tickable {
  tick(sim: any): boolean; // returns true if finished
}
