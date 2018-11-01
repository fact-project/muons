import numpy as np
from muons.muon_ring_simulation import compare_psf_fuzz as cpf


def test_paths():
    simulation_dir = "/home/titan/Desktop/Thesis/muons/muons/tests/"
    suffix = "**/*.sim.phs"
    np.testing.assert_equal(
        len(cpf.paths(simulation_dir, suffix)),
        1
    )


def test_get_simTruth1():
    simTruthPath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs.simulationtruth.csv"
    mu_event_ids = [1,2,3,4,5,6,7,8,9,10,11,12]
    point_spread_function = cpf.get_simTruth(simTruthPath, mu_event_ids)
    assert point_spread_function < 1


def test_run_fuzz_job():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.run_fuzz_job(inpath)
    np.testing.assert_equal(
        returns[2],
        11
    )


def test_with_one_PSF1():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.with_one_PSF(inpath)
    np.testing.assert_equal(
        len(returns),
        4
    )


def test_with_one_PSF2():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[1]])) == 1


def test_with_one_PSF3():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[2]])) == 1


def test_with_one_PSF4():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[3]])) == 1


def test_run_fuzz_job2():
    inpath = "/home/titan/Desktop/Thesis/muons/muons/tests/resources/simulation.sim.phs"
    returns = cpf.run_fuzz_job(inpath)
    assert returns[0] < 1
