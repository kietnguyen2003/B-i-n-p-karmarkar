"""[MS T16-T21; BC 4.2.3] Kernel projection, rank deficiency and tiny directions."""
import numpy as np
from karmarkar import *


def test_T16_empty_A():
    """[BC 4.4.4] With B=eT, p=v-mean(v)."""
    v=np.array([0.,2.,3.]);p,_=project_to_kernel(np.ones((1,3)),v)
    np.testing.assert_allclose(p,v-v.mean(),atol=1e-12)


def test_T17_full_row_rank():
    """[BC (4.15)] SVD agrees with full-row-rank analytic formula."""
    B=np.array([[1.,-1.,0.,0.],[1.,1.,1.,1.]])
    v=np.array([1.,3.,2.,5.]);p,info=project_to_kernel(B,v)
    expected=v-B.T@np.linalg.solve(B@B.T,B@v)
    np.testing.assert_allclose(p,expected,atol=1e-12)
    assert info["rank"]==2


def test_T18_dependent_rows():
    """[BC p41; MS C05] Duplicate constraints preserve the kernel."""
    B=np.array([[1.,-1.,0.],[2.,-2.,0.],[1.,1.,1.]])
    p,info=project_to_kernel(B,np.array([1.,2.,3.]))
    assert info["rank"]==2 and np.linalg.norm(B@p)<1e-12


def test_T19_empty_kernel():
    """[BC 4.3.5] A singleton feasible set does not imply objective zero."""
    p=CanonicalLP(np.array([[1.,-1.]]),np.array([0.,1.]))
    assert solve_karmarkar(p).status==StopReason.NO_PROJECTED_DIRECTION


def test_T20_tiny_scale():
    """[MS T20] Tiny p is numerical uncertainty, not an exact optimality proof."""
    p=CanonicalLP(np.empty((0,3)),1e-30*np.array([0.,1.,1.]))
    assert solve_karmarkar(p).status==StopReason.NUMERICALLY_UNDETERMINED


def test_T21_orthogonality():
    """[BC Mệnh đề 4.2.3] Remainder orthogonal to the whole nullspace."""
    p,info=project_to_kernel(np.array([[1.,-1.,0.],[1.,1.,1.]]),np.array([4.,2.,1.]))
    assert info["orthogonality_residual"]<1e-12
    assert info["equality_residual"]<1e-12

