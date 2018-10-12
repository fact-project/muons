import numpy as np'
from scipy import stats


def test_draw_inclination():
    size = 100000
    r = 1
    inclinations = rs.draw_inclination(
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
    azimuths = rs.draw_azimuth(
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
