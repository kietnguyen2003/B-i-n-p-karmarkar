"""[MS C11/M11, section 8; DX] Real-run benchmarks and INDEPENDENT HiGHS reference.

This is the only module that imports scipy.optimize.linprog. The core never calls
this module; reference solutions cannot enter Karmarkar iteration histories.
"""
from dataclasses import replace
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from .types import CanonicalLP, SolverConfig
from .examples import report_example_lp
from .canonical import validate_canonical, equality_residual
from .solver import solve_karmarkar
from .io import write_json, environment_manifest


def dataset_cases(seed: int = 20261028) -> list[CanonicalLP]:
    """[MS 8.2, F1-F8] Controlled families with witnesses, invalid and stress cases."""
    rng = np.random.default_rng(seed)
    cases = [replace(report_example_lp(), name="F1_source")]
    for n in (4, 8, 16, 32):
        c = rng.uniform(0.2, 2.0, n)
        c[0] = 0
        cases.append(CanonicalLP(np.empty((0,n)), c, f"F2_n{n}", zero_witness=np.eye(n)[0]))
    A, c, w = np.array([[1.,-1.,0.,0.]]), np.array([0.,0.,1.,1.]), np.array([.5,.5,0.,0.])
    cases.extend([
        CanonicalLP(A,c,"F3_equality",zero_witness=w),
        CanonicalLP(np.vstack((A,2*A,A)),c,"F4_dependent",zero_witness=w),
        CanonicalLP(np.array([[1.,-1.]]),np.array([0.,1.]),"F5_no_movement"),
        CanonicalLP(np.empty((0,4)),np.array([1.,2.,3.,4.]),"F6_positive_optimum"),
        CanonicalLP(np.empty((0,3)),np.ones(3),"F6_constant_positive"),
        CanonicalLP(np.array([[1.,0.,0.]]),np.array([0.,1.,1.]),"F7_Ae_invalid"),
        CanonicalLP(np.empty((0,3)),np.array([-3.,1.,1.]),"F7_center_invalid"),
        CanonicalLP(np.empty((0,3)),np.array([0.,np.nan,1.]),"F7_nan"),
        CanonicalLP(np.zeros(3),np.ones(3),"F7_shape"),
        CanonicalLP(np.array([[1.,-1.,0.,0.],[1.,-1.,1e-12,-1e-12]])*1e6,
                    c*1e-5,"F8_near_dependent",zero_witness=w),
        CanonicalLP(A*1e-8,c*1e5,"F8_scale",zero_witness=w),
    ])
    return cases


def solve_reference_with_highs(problem: CanonicalLP, method: str = "highs-ds") -> dict:
    """[MS 8.3; DX] Solve the SAME canonical LP outside the projective solver.

    INPUT: original canonical A,c. OUTPUT: objective, feasibility, native status,
    measured solver wall time and actual method. Not an iteration generator.
    """
    A, c = np.asarray(problem.A), np.asarray(problem.c)
    if A.ndim != 2 or c.ndim != 1 or A.shape[1] != c.size or not np.isfinite(A).all() or not np.isfinite(c).all():
        return {"success": False, "status": "invalid_shape_or_values", "method": method}
    Aeq = np.vstack((A,np.ones((1,c.size))))
    b = np.r_[np.zeros(A.shape[0]), 1.]
    start = perf_counter()
    result = linprog(c, A_eq=Aeq, b_eq=b, bounds=(0,None), method=method,
                     options={"primal_feasibility_tolerance": 1e-9,
                              "dual_feasibility_tolerance": 1e-9})
    elapsed = (perf_counter()-start)*1000
    return {"success": bool(result.success), "status": int(result.status), "message": result.message,
            "method": method, "elapsed_ms": elapsed, "iterations": int(result.nit),
            "objective": float(result.fun) if result.success else None,
            "x": result.x if result.success else None,
            "equality_residual": (float(np.max(np.abs(Aeq@result.x-b))) if result.success else None)}


def run_benchmark(cases: list[CanonicalLP], config: SolverConfig, repetitions: int,
                  seed: int, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """[MS 8.4,C11] Execute every case R times; retain failures and separate timers.

    Each measured Karmarkar run precedes its reference solve. Full first-run
    traces are serialized after timing. Memory is explicitly not measured.
    """
    if isinstance(repetitions,bool) or not isinstance(repetitions,int) or repetitions < 1:
        raise ValueError("repetitions must be an integer >=1")
    out = Path(output_dir)
    (out/"tables").mkdir(parents=True, exist_ok=True)
    rows = []
    # Warm up both backends once, outside all measurements.
    warm = report_example_lp()
    solve_karmarkar(warm,replace(config,max_iter=1))
    solve_reference_with_highs(warm)
    for case in cases:
        report = validate_canonical(case,config)
        A,c = np.asarray(case.A), np.asarray(case.c)
        for repeat in range(repetitions):
            start = perf_counter()
            run = solve_karmarkar(case,config)
            elapsed = (perf_counter()-start)*1000
            reference = solve_reference_with_highs(case) if report.valid else {"success":False,"status":"invalid_canonical_skipped"}
            row = {"case":case.name,"repeat":repeat,"n":int(c.size),"m":int(A.shape[0]) if A.ndim==2 else None,
                   "rank_A":report.rank_A,"nnz":int(np.count_nonzero(A)),
                   "A_norm":float(np.linalg.norm(A)),"c_norm":float(np.linalg.norm(c)),
                   "alpha":config.alpha,"epsilon":config.epsilon,"feas_tol":config.feas_tol,
                   "svd_rtol":config.svd_rtol,"svd_atol":config.svd_atol,"seed":seed,
                   "iter":run.iterations,"status":run.status.value,"objective":run.objective,
                   "elapsed_ms":elapsed,"reference_ms":reference.get("elapsed_ms"),
                   "reference_iter":reference.get("iterations"),
                   "reference_success":reference["success"],"reference_status":reference["status"],
                   "reference_method":reference.get("method"),"z_ref":reference.get("objective"),
                   "reference_gap":run.objective-reference["objective"] if reference.get("success") else None,
                   "min_x":float(run.x.min()) if run.x.size else None,
                   "feas":equality_residual(A,run.x) if report.valid else None,
                   "sum_residual":abs(float(run.x.sum())-1) if run.x.size else None,
                   "nonnegative":report.nonnegative.value,"zero_optimum_known":report.zero_optimum_known,
                   "theorem_scope":run.diagnostics["theorem_scope"]}
            rows.append(row)
            if repeat==0:
                write_json(out/"traces"/f"{case.name}.json",{"problem":case,"run":run,"reference":reference})
    data = pd.DataFrame(rows)
    data.to_csv(out/"tables"/"benchmark_results.csv",index=False,encoding="utf-8-sig")
    summary = data.groupby(["case","n","status"],dropna=False).agg(
        repetitions=("elapsed_ms","size"),median_ms=("elapsed_ms","median"),
        min_ms=("elapsed_ms","min"),max_ms=("elapsed_ms","max"),std_ms=("elapsed_ms","std"),
        median_iter=("iter","median"),reference_median_ms=("reference_ms","median"),
        reference_median_iter=("reference_iter","median"),
        objective=("objective","median"),reference_gap=("reference_gap","median")).reset_index()
    summary.to_csv(out/"tables"/"comparison_table.csv",index=False,encoding="utf-8-sig")
    manifest=environment_manifest(config,seed)
    manifest.update(repetitions=repetitions,case_names=[p.name for p in cases],
                    reference_options={"method":"highs-ds","primal_feasibility_tolerance":1e-9,"dual_feasibility_tolerance":1e-9},
                    fairness="Different stopping criteria/backends; timing is descriptive, not proof of algorithm superiority.")
    write_json(out/"run_manifest.json",manifest)
    return data,summary

