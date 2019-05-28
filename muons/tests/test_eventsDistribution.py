import numpy as np
from scipy import stats
from muons.muon_ring_simulation import eventsDistribution as ms


def test_draw_inclination():
    size = 100000
    r = 1
    inclinations = ms.draw_inclination(
        low=0,
        high=np.pi/2,
        size=size
    )
    h = [r*np.sin(i) for i in inclinations]
    uni = stats.kstest(
        h,
        "uniform",
        alternative="greater"
    )[1]
    np.testing.assert_almost_equal(
        uni,
        1,
        7
    )


def test_draw_azimuth():
    size = 100000
    r = 1
    azimuths = ms.draw_azimuth(
        low=0,
        high=np.pi,
        size=size
    )
    h = [r*np.sin(i) for i in azimuths]
    uni = stats.kstest(
        h,
        "uniform",
        alternative="greater"
    )[1]
    np.testing.assert_almost_equal(
        uni,
        1,
        7
    )


def test_casaul_trajectory1():
    np.testing.assert_equal(
        ms.casual_trajectory(
            muon_support_ground=np.array([0, 0, 0]),
            muon_direction_ground=np.array([0, 0, 1])
        )[1],
        [0, 0, -1]
    )


def test_casaul_trajectory2():
    np.testing.assert_equal(
        ms.casual_trajectory(
            muon_support_ground=np.array([0, 0, 0]),
            muon_direction_ground=np.array([0, 0, 1])
        )[0],
        [0, 0, 1000]
    )
