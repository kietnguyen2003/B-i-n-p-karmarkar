"""[MS T24-T25; BC 4.2.6] Log domain and invariant differences."""
import numpy as np
import pytest
from karmarkar import *


@pytest.mark.parametrize("x,c",[(np.array([1.,0.,0.]),np.ones(3)),(np.ones(3)/3,-np.ones(3)),(np.array([np.nan,.5,.5]),np.ones(3))])
def test_T24_log_domain(x,c):
    """[BC (4.29)] Invalid log arguments rejected before evaluation."""
    with pytest.raises(ValueError):
        potential(x,c)


def test_T25_invariant_differences():
    """[BC (4.30)-(4.31)] Absolute values differ, changes agree for fixed D."""
    a=np.array([.5,.25,.25]); c=np.array([0.,1.,1.])
    y0=np.ones(3)/3;y1=np.array([.4,.3,.3])
    x0=from_projective(a,y0);x1=from_projective(a,y1)
    assert np.isclose(potential(x1,c)-potential(x0,c),transformed_potential(a,y1,c)-transformed_potential(a,y0,c))
    assert np.isclose(potential(x1,c),transformed_potential(a,y1,c)-np.log(a).sum())

