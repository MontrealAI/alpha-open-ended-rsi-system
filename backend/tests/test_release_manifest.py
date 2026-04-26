import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_generate_provenance_manifest(tmp_path: Path):
    output = tmp_path / 'manifest-a.json'
    output_b = tmp_path / 'manifest-b.json'
    cmd = [
        'python',
        str(ROOT / 'scripts/release/generate_provenance_manifest.py'),
        '--tag',
        'v2.6.0-rc.1',
        '--output',
        str(output),
    ]
    subprocess.check_call(cmd, cwd=ROOT)
    cmd[-1] = str(output_b)
    subprocess.check_call(cmd, cwd=ROOT)

    data = json.loads(output.read_text())
    data_b = json.loads(output_b.read_text())
    assert data['release_tag'] == 'v2.6.0-rc.1'
    assert len(data['files']) > 10
    assert any(item['path'] == 'README.md' for item in data['files'])
    assert data == data_b
