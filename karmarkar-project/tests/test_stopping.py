"""[MS T32,T34,T35; BC 4.3.5] Scope and termination integration tests."""
import numpy as np
from karmarkar import *


def test_T32_positive_optimum():
    """[BC 4.3.5] Positive optimum never silently acquires a zero-optimum flag."""
    p=CanonicalLP(np.empty((0,3)),np.ones(3))
    r=solve_karmarkar(p,SolverConfig(epsilon=2))
    assert r.status==StopReason.NO_PROJECTED_DIRECTION
    assert not r.diagnostics["exact_optimality_certificate"]
    assert solve_karmarkar(p,SolverConfig(monitor_potential=True)).status==StopReason.PRECONDITION_UNVERIFIED


def test_T34_budget():
    """[BC Algorithm 4.1; MS C08] Budget exhaustion and complete trace."""
    r=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=3))
    assert r.status==StopReason.MAX_ITERATIONS and len(r.trace)==r.iterations==3


def test_T35_deterministic():
    """[MS T35] Same config/data yields the same actual trajectory."""
    a=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=10))
    b=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=10))
    np.testing.assert_allclose(a.x,b.x,atol=1e-14)


def test_approximation_and_monitor():
    """[BC 4.3.5] Numerical threshold success is labelled APPROX, never OPTIMAL."""
    r=solve_karmarkar(report_example_lp(),SolverConfig(epsilon=1e-6,monitor_potential=True))
    assert r.status==StopReason.APPROX_TOL_REACHED
    assert 0<=r.objective<=1e-6
    assert all(s.diagnostics["potential_decrease"]>=1/8-1e-9 for s in r.trace)

