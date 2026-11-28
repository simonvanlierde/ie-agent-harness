import numpy as np
import pytest

from toy_lca import (
    MASS_IN,
    PRODUCT_KG,
    WASTE_KG,
    A,
    B,
    C,
    impact,
    mass_imbalance,
    steel_footprint,
    to_kg,
)


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


def test_mass_balances():
    assert mass_imbalance(B, MASS_IN, PRODUCT_KG, WASTE_KG) == pytest.approx(
        0, abs=1e-9
    )


def test_mass_balance_names_the_broken_process():
    # Planted error: steel's CH4 emission is 10 times too high.
    bad_B = B.copy()
    bad_B[1, 1] *= 10
    gap = mass_imbalance(bad_B, MASS_IN, PRODUCT_KG, WASTE_KG)
    assert gap[0] == pytest.approx(0, abs=1e-9)
    assert gap[1] == pytest.approx(-0.09)
