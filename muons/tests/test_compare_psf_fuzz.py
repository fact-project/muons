import numpy as np
from muons.analysis_utensils.simulation_analysis.simulation_utensils import(
    compare_psf_fuzz as cpf)
import os
dirname = os.path.dirname(__file__)


def test_paths():
    simulation_dir = dirname
    suffix = "**/*.sim.phs"
    np.testing.assert_equal(
        len(cpf.paths(simulation_dir, suffix)),
        1
    )


def test_get_simTruth1():
    simTruthPath = os.path.join(dirname, "resources/100simulations_psf0.0.simulationtruth.csv")
    mu_event_ids = [1,2,3,4,5,6,7,8,9,10,11,12]
    point_spread_function = cpf.get_simTruth(simTruthPath, mu_event_ids)
    assert point_spread_function < 1


def test_run_fuzz_job():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.run_fuzz_job(inpath)
    np.testing.assert_equal(
        returns[2],
        10
    )


def test_with_one_PSF1():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.with_one_PSF(inpath)
    np.testing.assert_equal(
        len(returns),
        4
    )


def test_with_one_PSF2():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[1]])) == 1


def test_with_one_PSF3():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[2]])) == 1


def test_with_one_PSF4():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.with_one_PSF(inpath)
    assert len(np.array([returns[3]])) == 1


def test_run_fuzz_job2():
    inpath = os.path.join(dirname, "resources/100simulations_psf0.0.sim.phs")
    returns = cpf.run_fuzz_job(inpath)
    assert returns[0] < 1
