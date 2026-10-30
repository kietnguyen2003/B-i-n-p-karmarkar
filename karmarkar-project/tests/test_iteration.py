"""[MS T22-T23,T31,T33; BC Mệnh đề 4.3.1] Actual step invariants."""
import numpy as np
from karmarkar import *


def test_T22_ball_step():
    """[BC (4.27)] Length alpha*r and strict positivity."""
    a,r,_=simplex_geometry(3);s=karmarkar_step(report_example_lp(),a,SolverConfig())
    assert s.status is None and np.all(s.y>0)
    assert np.isclose(np.linalg.norm(s.y-a),.25*r)


def test_T23_feasibility():
    """[BC (4.41)] Inverse keeps simplex positivity and unit sum."""
    run=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=20))
    for s in run.trace:
        assert s.status is None and np.min(s.x_after)>0
        assert abs(s.x_after.sum()-1)<1e-12


def test_T31_additional_equality():
    """[MS F3; BC (4.37)] Nonempty A must actually enter AD."""
    p=CanonicalLP(np.array([[1.,-1.,0.,0.]]),np.array([0.,0.,1.,1.]),zero_witness=np.array([.5,.5,0.,0.]))
    r=solve_karmarkar(p,SolverConfig(max_iter=30))
    assert r.iterations==30
    for s in r.trace:
        np.testing.assert_allclose(p.A@s.x_after,0,atol=1e-12)
        np.testing.assert_allclose(s.B[:-1],p.A@s.D,atol=1e-12)


def test_AD_at_nonsymmetric_interior_point():
    """[MS section 9] Regression: dropping D can pass F3 by symmetry; break symmetry."""
    p=CanonicalLP(np.array([[1.,-1.,1.,-1.]]),np.array([0.,0.,1.,1.]))
    x=np.array([.4,.1,.1,.4]);s=karmarkar_step(p,x,SolverConfig())
    assert s.status is None
    assert np.linalg.norm(p.A@s.x_after)<1e-12
    assert not np.allclose(s.B[:-1],p.A)


def test_T33_distinct_coordinates():
    """[BC 4.4.6] Only at initial center does inverse cancel its uniform scale."""
    p=report_example_lp();s0=karmarkar_step(p,np.ones(3)/3,SolverConfig())
    s1=karmarkar_step(p,s0.x_after,SolverConfig(),k=1)
    assert not np.allclose(s1.y,s1.x_after)
    np.testing.assert_allclose(s1.D,np.diag(s0.x_after))

