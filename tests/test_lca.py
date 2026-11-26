import numpy as np
import pytest

from toy_lca import A, B, C, impact, steel_footprint, to_kg


def test_kg_and_tonnes_agree():
    assert steel_footprint(0.1, "t") == pytest.approx(steel_footprint(100, "kg"))


def test_to_kg():
    assert to_kg(2, "t") == 2000
    with pytest.raises(KeyError):
        to_kg(1, "lb")


def test_footprint_scales_linearly():
    assert steel_footprint(200) == pytest.approx(2 * steel_footprint(100))


def test_matrix_shapes_chain():
    assert A.shape == (2, 2)
    assert B.shape == (2, 2)
    assert C.shape == (1, 2)


def test_bad_shapes_are_refused():
    with pytest.raises(ValueError, match="shapes do not chain"):
        impact(A, B, C, np.array([1.0, 2.0, 3.0]))
