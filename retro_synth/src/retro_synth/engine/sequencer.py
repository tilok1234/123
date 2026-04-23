from typing import List, Dict, Any

class Sequencer:
    def __init__(self, command_bus, sr=48000):
        self.command_bus = command_bus
        self.sr = sr
        self.bpm = 120
        self.rows_per_beat = 4

        self.playing = False
        self.current_order = 0
        self.current_row = 0
        self.samples_per_row = self._calc_samples_per_row()
        self.sample_counter = 0

        self.project = None

    def _calc_samples_per_row(self):
        beats_per_sec = self.bpm / 60.0
        rows_per_sec = beats_per_sec * self.rows_per_beat
        return int(self.sr / rows_per_sec)

    def set_project(self, project):
        self.project = project

    def play(self):
        self.playing = True
        self.sample_counter = self.samples_per_row # force tick on start

    def stop(self):
        self.playing = False

    def seek(self, order, row):
        self.current_order = order
        self.current_row = row
        self.sample_counter = self.samples_per_row

    def advance(self, frames: int):
        if not self.playing or not self.project:
            return

        remaining = frames
        while remaining > 0:
            if self.sample_counter >= self.samples_per_row:
                self._tick()
                self.sample_counter = 0

            step = min(remaining, self.samples_per_row - self.sample_counter)
            self.sample_counter += step
            remaining -= step

    def _tick(self):
        if self.current_order >= len(self.project.orders):
            self.stop()
            return

        pattern_name = f"pattern_{self.project.orders[self.current_order]:02d}"
        if pattern_name in self.project.patterns:
            pattern = self.project.patterns[pattern_name]

            for ev in pattern.get("events", []):
                if ev.get("row") == self.current_row:
                    self._dispatch_event(ev)

            self.current_row += 1
            if self.current_row >= pattern.get("rows", 64):
                self.current_row = 0
                self.current_order += 1

    def _dispatch_event(self, ev: Dict[str, Any]):
        note_str = ev.get("note")
        if not note_str:
            return

        # Simplistic note parsing e.g. "C-4" -> 60
        note_names = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
        note_idx = note_names.index(note_str[:2])
        octave = int(note_str[2])
        midi_note = (octave + 1) * 12 + note_idx

        inst_name = ev.get("inst")
        if inst_name and inst_name in self.project.instruments:
            inst = self.project.instruments[inst_name]
            engine_type = inst.get("engine")
            vel = ev.get("vol", 100)

            if engine_type == "fm4op":
                self.command_bus.push(("fm_note_on", midi_note, vel, inst))
            elif engine_type == "pcm":
                self.command_bus.push(("pcm_trigger", inst_name, midi_note, vel))
            elif engine_type == "wavetable":
                 import numpy as np
                 # Dummy sine table for now
                 table = np.sin(np.linspace(0, 2*np.pi, 2048, endpoint=False))
                 self.command_bus.push(("wt_note_on", midi_note, vel, table))
