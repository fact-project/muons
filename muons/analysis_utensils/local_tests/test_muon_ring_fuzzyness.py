import numpy as np
from muons.analysis_utensils.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf


def test_standard_deviation():
    point_cloud = np.array([[0, 1], [1, 0], [0, 1], [1, 0]])
    muon_props = {
        "muon_ring_cx": [0, 1, 0, 1],
        "muon_ring_cy": [1, 0, 1, 0],
        "muon_ring_r": [1, 1, 1, 1]
    }
    np.testing.assert_equal(
        mrf.standard_deviation(
            point_cloud,
            muon_props
        ),
        0
    )
