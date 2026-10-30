"""[MS T10, NB15-NB16; BC 4.2.2] Geometry invariants."""
import numpy as np
import pytest
from karmarkar import simplex_geometry, simplex_embedding


@pytest.mark.parametrize("n",[2,3,4,10])
def test_T10_radii(n):
    """[BC (4.11)-(4.12)] Correct radii and ratio n-1."""
    a,r,R=simplex_geometry(n)
    assert np.isclose(a.sum(),1) and np.all(a>0)
    assert np.isclose(R/r,n-1)
    assert np.isclose(np.linalg.norm(np.eye(n)[0]-a),R)


def test_embedding_preserves_metric():
    """[MS 7.1, Fig 4.3] Screen geometry must preserve the simplex metric."""
    u=np.array([[.1,.2,.7],[.4,.4,.2]])
    assert np.isclose(np.linalg.norm(u[0]-u[1]),np.linalg.norm(simplex_embedding(u)[0]-simplex_embedding(u)[1]))

