"""[MS T26-T30; BC 4.4.3-4.4.10] Golden values are assertions, never solver outputs."""
import numpy as np
from karmarkar import *


def test_T26_first_step():
    """[BC (4.49)-(4.51)] Full first-step fixture."""
    s=karmarkar_step(report_example_lp(),np.ones(3)/3,SolverConfig())
    np.testing.assert_allclose(s.p,np.array([-2,1,1])/9,atol=1e-12)
    np.testing.assert_allclose(s.d,np.array([2,-1,-1])/np.sqrt(6),atol=1e-12)
    np.testing.assert_allclose(s.x_after,np.array([10,7,7])/24,atol=1e-12)


def test_T27_second_step():
    """[BC (4.52)] u2 and z2."""
    r=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=2))
    np.testing.assert_allclose(r.x,np.array([100,49,49])/198,atol=1e-12)
    np.testing.assert_allclose(r.trace[1].p,7*np.array([-2,1,1])/72,atol=1e-12)
    assert np.isclose(2*r.objective,98/99)


def test_T28_third_step():
    """[BC (4.53)] u3 and z3."""
    r=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=3))
    np.testing.assert_allclose(r.x,np.array([1000,343,343])/1686,atol=1e-12)
    assert np.isclose(2*r.objective,686/843)


def test_T29_closed_form_and_table():
    """[BC (4.54)-(4.55), Table 4.2] Compare independent oracle to actual traces."""
    r=solve_karmarkar(report_example_lp(),SolverConfig(max_iter=20))
    printed=np.array([[.666667,.666667,1.333333],[.833333,.583333,1.166667],
                      [1.010101,.494949,.989899],[1.186240,.406880,.813760],
                      [1.893052,.053474,.106948],[1.996813,.001593,.003187]])
    points=[r.trace[0].x_before]+[s.x_after for s in r.trace]
    for j,k in enumerate([0,1,2,3,10,20]):
        np.testing.assert_allclose(points[k],analytic_u(k),atol=1e-9)
        np.testing.assert_allclose(np.r_[u_to_original(points[k]),2*points[k][1:].sum()],printed[j],atol=5e-6)


def test_T30_potential_and_stopping():
    """[BC (4.56)-(4.57)] Exact potential formula and least original-z threshold k."""
    for k in [0,1,2,3,10,20]:
        assert np.isclose(potential(analytic_u(k),np.array([0,1,1])),analytic_potential(k))
    assert np.isclose(analytic_potential(1)-analytic_potential(0),np.log(.7))
    assert minimum_example_iterations(.1)==11
    assert analytic_objective(10)>.1 and analytic_objective(11)<=.1


def test_slack_roundtrip():
    """[BC (4.44)-(4.46)] Original coordinates and canonical objective scaling."""
    for x in [(0,0),(2,0),(.5,.5)]:
        u=original_to_u(*x)
        np.testing.assert_allclose(u_to_original(u),x)
        assert np.isclose(2*u[1:].sum(),2-x[0])

