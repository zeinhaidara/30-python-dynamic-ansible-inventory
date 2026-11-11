import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "inventory.py"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_host_returns_empty_object():
    result = _run("--host", "anything")

    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_list_without_credentials_fails_loudly_not_silently():
    env_without_creds = {
        "PATH": __import__("os").environ.get("PATH", ""),
        "AWS_ACCESS_KEY_ID": "",
        "AWS_SECRET_ACCESS_KEY": "",
        "AWS_SESSION_TOKEN": "",
        "AWS_PROFILE": "nonexistent-profile-does-not-exist",
        "AWS_EC2_METADATA_DISABLED": "true",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        env=env_without_creds,
    )

    assert result.returncode != 0
    assert result.stdout.strip() == ""
    assert "inventory:" in result.stderr
