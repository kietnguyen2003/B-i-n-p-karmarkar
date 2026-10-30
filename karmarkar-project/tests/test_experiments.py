"""[MS C11,8.2-8.4] Real reference isolation, failure retention and evidence export."""
import ast
import json
from pathlib import Path
import numpy as np
from karmarkar import *
from karmarkar.experiments import dataset_cases, run_benchmark, solve_reference_with_highs


def test_reference_and_core_isolation():
    """[MS section 9] Core AST imports cannot depend on reference LP or experiments."""
    import karmarkar
    root=Path(karmarkar.__file__).parent
    for name in ["iteration.py","solver.py","projection.py","canonical.py"]:
        tree=ast.parse((root/name).read_text(encoding="utf-8"))
        imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        assert all("optimize" not in s and "experiments" not in s for s in imports)
    p=report_example_lp();ref=solve_reference_with_highs(p)
    assert ref["success"] and abs(ref["objective"])<1e-12


def test_benchmark_retains_failures_and_manifest(tmp_path):
    """[MS 8.4] Actual repeated runs export raw rows, full traces and environment."""
    cases=dataset_cases()[:2]+[dataset_cases()[10]]
    data,summary=run_benchmark(cases,SolverConfig(max_iter=2),2,42,tmp_path)
    assert len(data)==6 and len(summary)==3
    assert "invalid_input" in set(data.status)
    assert (tmp_path/"tables/benchmark_results.csv").exists()
    manifest=json.loads((tmp_path/"run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["seed"]==42 and manifest["repetitions"]==2
    assert manifest["versions"]["scipy"]

