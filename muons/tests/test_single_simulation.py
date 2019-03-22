import numpy as np
from muons.muon_ring_simulation import single_simulation as rs
import photon_stream as ps
from scipy import stats

np.random.seed(seed=1)


def test_do_not_raise_exception():
    photon_pos, photon_dir = rs.emit_photons(
        np.array([0, 0, 1000]),
        np.array([0, 0, -1]),
        np.deg2rad(1.2),
        ch_rate=1
    )
    xys = rs.project_ch_photon_on_ground(photon_pos, photon_dir)
    np.testing.assert_almost_equal(xys[:, 2], 0, 3)


def test_simple_photons():
    photon_pos = np.array([
        [0, 0, 100],
        [1, 0, 100],
        [0, 1, 100],
        [0, 2, 150]])
    photon_dir = np.array([
        [0, 0, -1],
        [0, 0, -1],
        [0, 0, -1],
        [0, 0, -1]])
    xys = rs.project_ch_photon_on_ground(photon_pos, photon_dir)
    assert xys.shape == (4, 3)
    np.testing.assert_array_almost_equal(xys[0, :], [0, 0, 0], decimal=6)
    np.testing.assert_array_almost_equal(xys[1, :], [1, 0, 0], decimal=6)
    np.testing.assert_array_almost_equal(xys[2, :], [0, 1, 0], decimal=6)
    np.testing.assert_array_almost_equal(xys[3, :], [0, 2, 0], decimal=6)


def test_pol2cart1():
    np.testing.assert_almost_equal(
        rs.pol2cart(r=1, azimuth=0, inclination=0),
        (0, 0, 1),
        16
    )


def test_pol2cart2():
    np.testing.assert_almost_equal(
        rs.pol2cart(r=1, azimuth=0.5*np.pi, inclination=0.5*np.pi),
        (0, 1, 0),
        16
    )


def test_pol2cart3():
    np.testing.assert_almost_equal(
        rs.pol2cart(r=1, azimuth=0, inclination=0.5*np.pi),
        (1, 0, 0),
        16
    )


def test_emit_photons():
    np.testing.assert_almost_equal(
        len(
            rs.emit_photons(
                casual_muon_support=[0, 1.5, 3000],
                casual_muon_direction=[0, 0, -1],
                opening_angle=np.deg2rad(1.2),
                ch_rate=3)[0]
        ),
        9000,
        decimal=-3
    )


def test_draw_direction_for_cherenkov_photon1():
    x = rs.draw_direction_of_cherenkov_photon(
            opening_angle=np.deg2rad(1.2),
            u=np.array([1, 0, 0]),
            v=np.array([0, 1, 0]),
            casual_muon_direction=np.array([0, 0, -1])
    )
    np.testing.assert_almost_equal(
        np.arccos(np.dot(x, np.array([0, 0, -1]))),
        np.deg2rad(1.2)
    )


def test_draw_direction_for_cherenkov_photon2():
    np.testing.assert_almost_equal(
        rs.draw_direction_of_cherenkov_photon(
            opening_angle=np.deg2rad(0.01),
            u=np.array([1, 0, 0]),
            v=np.array([0, 1, 0]),
            casual_muon_direction=np.array([0, 0, -1])
        ),
        [0, 0, -1],
        3
    )


def test_get_u_v1():
    np.testing.assert_equal(
        np.dot(
            np.array(rs.get_u_v(direction=[0, 0, -1]))[0],
            [0, 0, -1]
        ),
        0
    )


def test_get_u_v2():
    np.testing.assert_equal(
        np.dot(
            np.array(rs.get_u_v([0, 0, -1]))[1],
            [0, 0, -1]
        ),
        0
    )


def test_get_u_v3():
    np.testing.assert_equal(
        np.dot(
            np.array(rs.get_u_v([0, 0, -1]))[0],
            np.array(rs.get_u_v([0, 0, -1]))[1]
        ),
        0
    )


def test_position_on_ray():
    np.testing.assert_equal(
        rs.position_on_ray(
            support=np.array([0, 0, 0]),
            direction=np.array([0, 0, 1]),
            alpha=1000),
        [0, 0, 1000]
    )


def test_mask_for_photons_in_aperture_radius():
    np.testing.assert_equal(
        rs.mask_for_photons_in_aperture_radius(
            intersection_point_on_xy_plane=np.array(
                [[0, 0, 0], [0, 4, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
            ),
            aperture_radius=3
        ),
        np.array([True, False, True, True, True])
    )


def test_perfect_imaging():
    np.testing.assert_equal(
        rs.perfect_imaging(
            photon_emission_positions=np.array(
                [
                    [0, 0, 1000],
                    [0, 0, 0],
                    [0, 0, 1],
                    [0, 0, 1],
                    [0, 0, 1]
                ]
            ),
            photon_directions=np.array(
                [
                    [0, 0, -1],
                    [1000, -1, -1],
                    [1, 0, -1],
                    [0, 1, -1],
                    [5, 4, -1]
                ]
            ),
            aperture_radius = 4
        ),
        np.array(
            [[0, 0], [1000, -1], [1, 0], [0, 1]]
        )
    )


def test_create_raw_photon_stream():
    nsb_rate_per_pixel = 35e6
    raw = rs.create_raw_photon_stream(
        pixel_CHIDs=np.array([]),
        arrival_times=np.array([]),
        nsb_rate_per_pixel=nsb_rate_per_pixel)
    nr = raw != ps.io.binary.LINEBREAK
    number_photons = np.sum(nr)
    expected_photon_number = 1440*nsb_rate_per_pixel*50e-9
    np.testing.assert_almost_equal(
        number_photons,
        expected_photon_number,
        -2
    )


def test_project_ch_photon_on_ground():
    np.testing.assert_equal(
        rs.project_ch_photon_on_ground(
            photon_emission_positions=np.array([
                np.array([0, 0, 1000]),
                np.array([0, 0, 0])
            ]),
            photon_directions=np.array([
                np.array([0, 0, -1]),
                np.array([-1, -1, -1])
            ])
        ),
        np.array([np.array([0, 0, 0]), np.array([0, 0, 0])])
    )


def test_artificial_point_spread_function():
    psf = rs.artificial_point_spread_function(
        number_photons=1000,
        standard_dev=0)
    assert psf.shape[0] == 1000
    assert psf.shape[1] == 2
    np.testing.assert_equal(psf, np.zeros(shape=(1000, 2)))
    
    psf = rs.artificial_point_spread_function(
        number_photons=1000,
        standard_dev=1)
    assert psf.shape[0] == 1000
    assert psf.shape[1] == 2
    np.testing.assert_almost_equal(np.std(psf[:, 0]), 1.0, 1)
    np.testing.assert_almost_equal(np.std(psf[:, 1]), 1.0, 1)


