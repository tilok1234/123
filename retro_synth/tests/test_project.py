import os
from retro_synth.io.project import ProjectModel, save_project, load_project

def test_project_save_load():
    proj = ProjectModel()
    proj.orders = [0, 1, 0, 2]
    proj.instruments["bass_fm"] = {
        "version": 1,
        "engine": "fm4op",
        "name": "Bass FM",
        "algorithm": 3
    }
    proj.patterns["pattern_00"] = {
        "rows": 64,
        "channels": 8,
        "events": [
            {"row": 0, "ch": 0, "note": "C-4", "inst": "bass_fm", "vol": 96}
        ]
    }

    test_path = "test_song.vgm16proj"
    save_project(proj, test_path)

    loaded_proj = load_project(test_path)
    assert loaded_proj.orders == [0, 1, 0, 2]
    assert loaded_proj.instruments["bass_fm"]["algorithm"] == 3
    assert loaded_proj.patterns["pattern_00"]["rows"] == 64

    os.remove(test_path)
    print("Project save/load test passed.")

if __name__ == "__main__":
    test_project_save_load()
