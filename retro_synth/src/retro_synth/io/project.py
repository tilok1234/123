import json
import os
import zipfile
from typing import Dict, Any

class ProjectModel:
    def __init__(self):
        self.version = 1
        self.instruments: Dict[str, Any] = {}
        self.patterns: Dict[str, Any] = {}
        self.samples: Dict[str, str] = {} # Name to path mapping
        self.orders = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "orders": self.orders
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        proj = cls()
        proj.version = data.get("version", 1)
        proj.orders = data.get("orders", [])
        return proj

def save_project(project: ProjectModel, path: str):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('project.json', json.dumps(project.to_dict(), indent=2))

        for name, inst in project.instruments.items():
            zf.writestr(f'instruments/{name}.json', json.dumps(inst, indent=2))

        for name, pat in project.patterns.items():
            zf.writestr(f'patterns/{name}.json', json.dumps(pat, indent=2))

        for name, sample_path in project.samples.items():
            if os.path.exists(sample_path):
                zf.write(sample_path, f'samples/{os.path.basename(sample_path)}')

def load_project(path: str) -> ProjectModel:
    project = ProjectModel()
    with zipfile.ZipFile(path, 'r') as zf:
        if 'project.json' in zf.namelist():
            data = json.loads(zf.read('project.json'))
            project = ProjectModel.from_dict(data)

        for name in zf.namelist():
            if name.startswith('instruments/') and name.endswith('.json'):
                inst_name = name[len('instruments/'):-5]
                project.instruments[inst_name] = json.loads(zf.read(name))
            elif name.startswith('patterns/') and name.endswith('.json'):
                pat_name = name[len('patterns/'):-5]
                project.patterns[pat_name] = json.loads(zf.read(name))
            elif name.startswith('samples/'):
                # Extract sample locally to a temp dir or handle in memory,
                # but for simplicity we keep track of the internal zip path
                pass

    return project
