"""[MS C11-C12, 7.2] Portable config, structured JSON, actual-run manifest."""
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import numpy as np
import yaml
from .types import SolverConfig


def plain(value):
    """[MS 7.2] Convert complete dataclass traces to strict JSON-compatible values."""
    if is_dataclass(value):
        return plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, (np.integer, np.floating)):
        return plain(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, value) -> None:
    """[MS 7.2] UTF-8 JSON with explicit null instead of nonstandard NaN/Infinity."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def load_config(path: Path) -> tuple[SolverConfig, dict]:
    """[MS 2.2,C12] Separate solver options from seed and repetition options."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    fields = SolverConfig.__dataclass_fields__
    unknown = set(raw)-set(fields)-{"seed", "repetitions"}
    if unknown:
        raise ValueError(f"unknown config keys: {unknown}")
    return SolverConfig(**{k: v for k, v in raw.items() if k in fields}), raw


def environment_manifest(config=None, seed=None) -> dict:
    """[MS 8.4] Record actual software, machine, local timestamp, config and source hashes."""
    versions = {name: importlib.metadata.version(name) for name in
                ("numpy", "scipy", "matplotlib", "pandas", "pytest", "nbformat", "nbclient")}
    settings = plain(config) if config else {}
    root = Path(__file__).resolve().parents[2]
    sources = {}
    for name in ("BC - Mục 4 - Karmarkar.pdf", "Karmarkar_Codex_MasterSpec.pdf"):
        p = root.parent/name
        if p.is_file():
            sources[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    git_executable = shutil.which("git")
    git = (subprocess.run([git_executable, "rev-parse", "HEAD"], cwd=root,
                          capture_output=True, text=True, check=False)
           if git_executable else None)
    return {"timestamp": datetime.now(timezone(timedelta(hours=7))).isoformat(),
            "timezone": "Asia/Saigon", "python": sys.version, "executable": sys.executable,
            "versions": versions, "machine": platform.platform(), "processor": platform.processor(),
            "seed": seed, "config": settings,
            "config_hash": hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest(),
            "git_commit": git.stdout.strip() if git and git.returncode == 0 else None,
            "source_sha256": sources,
            "timing_scope": "solver only; excludes import, plotting and serialization",
            "memory": "not measured", "exact_optimality_certificate": False}

