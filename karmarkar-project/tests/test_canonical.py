"""[MS section 6, T01-T09; BC 4.2.1,4.3.1] Input and scope tests."""
from dataclasses import replace
import numpy as np
import pytest
from karmarkar import *


def test_T01_reject_n_one():
    """[T01; BC (4.2)] n>=2."""
    assert not validate_canonical(CanonicalLP(np.empty((0,1)),np.ones(1)),SolverConfig()).valid


@pytest.mark.parametrize("A",[np.zeros(3),np.zeros((1,2))])
def test_T02_shape(A):
    """[T02; MS 2.2] A is always 2D with n columns."""
    assert solve_karmarkar(CanonicalLP(A,np.ones(3))).status==StopReason.INVALID_INPUT


@pytest.mark.parametrize("bad",[np.nan,np.inf,-np.inf])
def test_T03_nonfinite(bad):
    """[T03; MS C02] No nonfinite input reaches iteration."""
    assert not validate_canonical(CanonicalLP(np.empty((0,3)),np.array([0,bad,1])),SolverConfig()).valid


def test_T04_Ae():
    """[T04; BC (4.7)] Center feasibility is required."""
    assert not validate_canonical(CanonicalLP(np.array([[1.,0.,0.]]),np.ones(3)),SolverConfig()).valid


def test_T05_center_objective():
    """[T05; BC (4.8)] Positive center objective required by this formulation."""
    assert not validate_canonical(CanonicalLP(np.empty((0,3)),-np.ones(3)),SolverConfig()).valid


def test_T06_certificate():
    """[T06; MS 2.2] Nonnegative c proves nonnegative objective over simplex."""
    v=validate_canonical(report_example_lp(),SolverConfig())
    assert v.nonnegative==ProofStatus.PROVEN and v.zero_optimum_known


def test_T07_unknown_not_proven():
    """[T07; MS 2.2] A positive center does not establish a global bound."""
    p=CanonicalLP(np.empty((0,3)),np.array([-1.,2.,2.]))
    assert validate_canonical(p,SolverConfig()).nonnegative==ProofStatus.UNKNOWN
    assert solve_karmarkar(p).status==StopReason.PRECONDITION_UNVERIFIED
    assert solve_karmarkar(p,SolverConfig(allow_unverified_demo=True,max_iter=1)).status!=StopReason.APPROX_TOL_REACHED


@pytest.mark.parametrize("alpha",[0,1,-1,1.1,float("nan")])
def test_T08_alpha(alpha):
    """[T08; BC 4.3.1] Strictly interior alpha."""
    assert not validate_canonical(report_example_lp(),SolverConfig(alpha=alpha)).valid


@pytest.mark.parametrize("max_iter",[-1,.2,True,np.inf])
def test_T09_maxiter(max_iter):
    """[T09; MS 2.2] Iteration budget is an integer >=0, never silently expanded."""
    assert not validate_canonical(report_example_lp(),SolverConfig(max_iter=max_iter)).valid


def test_negative_and_dual_certificates():
    """[MS 2.2, GD] Validate actual negative and dual witnesses, including failures."""
    p=CanonicalLP(np.empty((0,3)),np.array([-1.,2.,2.]),negative_witness=np.array([1.,0.,0.]))
    assert validate_canonical(p,SolverConfig()).nonnegative==ProofStatus.DISPROVEN
    A=np.array([[1.,-1.,0.]])
    p=CanonicalLP(A,np.array([-1.,1.,1.]),dual_multiplier=np.array([-1.]))
    assert validate_canonical(p,SolverConfig()).nonnegative==ProofStatus.PROVEN
    assert not validate_canonical(replace(p,dual_multiplier=np.array([1.])),SolverConfig()).valid


def test_small_costs_do_not_fabricate_zero_optimum():
    """[MS 2.2, T32] Absolute tolerance must not certify tiny positive costs as zero."""
    p=CanonicalLP(np.empty((0,3)),1e-25*np.ones(3),zero_witness=np.array([1.,0.,0.]))
    v=validate_canonical(p,SolverConfig())
    assert not v.valid and not v.zero_optimum_known

