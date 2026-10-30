"""[MS T11-T15; BC 4.2.4] Fixed-reference transformation tests."""
import numpy as np
import pytest
from karmarkar import to_projective, from_projective

a=np.array([.5,.25,.25])
b=np.array([2/3,1/6,1/6])


def test_T11_center():
    """[BC Mệnh đề 4.2.4(iii)] T_a(a)=a0."""
    np.testing.assert_allclose(to_projective(a,a),np.ones(3)/3,atol=1e-12)


def test_T12_other_point():
    """[BC p43] The same fixed reference sends b to a, not the center."""
    np.testing.assert_allclose(to_projective(a,b),a,atol=1e-12)


def test_T13_roundtrip():
    """[BC (4.19)-(4.21)] Inverse exactly undoes fixed-reference map numerically."""
    np.testing.assert_allclose(from_projective(a,to_projective(a,b)),b,atol=1e-12)


def test_T14_zero_reference():
    """[MS T14] A boundary point cannot define invertible D."""
    with pytest.raises(ValueError):
        to_projective(np.array([1.,0.,0.]),b)


def test_T15_fractional_objective():
    """[BC (4.22)] Compare true fractional objective, not the linear surrogate."""
    c=np.array([0.,1.,2.]); y=to_projective(a,b)
    assert np.isclose(c@b,(a*c)@y/(a@y))
    assert not np.isclose(c@b,(a*c)@y)

