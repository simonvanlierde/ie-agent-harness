"""Toy matrix LCA: h = C @ B @ inv(A) @ f.

All numbers are made up for teaching. They are not data for any real product.
"""

import numpy as np

# Processes (columns) and products (rows): electricity [kWh], steel [kg].
# A[i, j] is the amount of product i that process j makes (+) or uses (-)
# per unit of its own output. Making 1 kg steel uses 1.5 kWh electricity.
A = np.array(
    [
        [1.0, -1.5],
        [0.0, 1.0],
    ]
)

# Emissions (rows) per unit of process output (columns), in kg: CO2, CH4.
B = np.array(
    [
        [0.5, 1.0],
        [0.002, 0.01],
    ]
)

# Characterisation: kg CO2-equivalent per kg of emission (CO2, CH4).
# The CH4 factor is a round teaching number, not a published GWP.
C = np.array([[1.0, 28.0]])

UNIT_TO_KG = {"kg": 1.0, "t": 1000.0}


def to_kg(amount: float, unit: str) -> float:
    """Convert a mass to kg. Raises KeyError for an unknown unit."""
    return amount * UNIT_TO_KG[unit]


def impact(A, B, C, f):
    """Impact vector h = C B A^-1 f, in the units of C's rows (kg CO2e here)."""
    A, B, C, f = (np.asarray(x, dtype=float) for x in (A, B, C, f))
    if A.shape[0] != A.shape[1]:
        raise ValueError(f"A must be square, got {A.shape}")
    if B.shape[1] != A.shape[0] or C.shape[1] != B.shape[0] or f.shape != (A.shape[0],):
        raise ValueError(
            f"shapes do not chain: A{A.shape} B{B.shape} C{C.shape} f{f.shape}"
        )
    scaling = np.linalg.solve(A, f)  # A^-1 f, without forming the inverse
    return C @ B @ scaling


def steel_footprint(amount: float, unit: str = "kg") -> float:
    """kg CO2e for the given mass of steel."""
    f = np.array([0.0, to_kg(amount, unit)])
    return float(impact(A, B, C, f)[0])
