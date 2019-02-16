import sys
import os
import shutil
import glob
from muons.analysis_utensils.simulation_analysis import (
    extract_muons_from_single_run as emf)
import pandas

filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
simulationFile = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.sim.phs")
simulationTruth = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.simulationtruth.csv")
output_dir = os.path.join(fileDir, "resources", "testDir")


def test_check_inputValidity_allCorrect():
    error = False
    try:
        Analysis = emf.SingleRunAnalysis(
            simulationFile, simulationTruth, output_dir)
        Analysis.check_inputValidity()
    except ValueError:
        error = True
    assert error == False


def test_check_inputValidity_wrongSimFile():
    error = False
    try:
        Analysis = emf.SingleRunAnalysis(
            "/foo/bar", simulationTruth, output_dir)
        Analysis.check_inputValidity()
    except ValueError:
        error = True
    assert error == True


def test_check_inputValidity_wrongSimTruth():
    error = False
    try:
        Analysis = emf.SingleRunAnalysis(
            simulationFile, "/foo/bar", output_dir)
        Analysis.check_inputValidity()
    except ValueError:
        error = True
    assert error == True


def test_check_inputValidity_wrongOut():
    error = False
    try:
        Analysis = emf.SingleRunAnalysis(
            simulationFile, simulationTruth, 5)
        Analysis.check_inputValidity()
    except (ValueError, TypeError):
        error = True
    assert error == True


def test_create_output_dir():
    Analysis = emf.SingleRunAnalysis(
        simulationFile, simulationTruth, output_dir)
    Analysis.create_output_dir()
    assert os.path.isdir(output_dir)


def test_extract_muons_from_run():
    Analysis = emf.SingleRunAnalysis(
        simulationFile, simulationTruth, output_dir)
    Analysis.extract_muons_from_run()
    muonsPath = os.path.join(output_dir, "extracted_muons.csv")
    assert os.path.exists(muonsPath)


def test_do_plotting():
    Analysis = emf.SingleRunAnalysis(
        simulationFile, simulationTruth, output_dir)
    Analysis.do_plotting()
    wild_card_path = os.path.join(output_dir, "Plots", "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 7


def test_analysis_main():
    Analysis = emf.SingleRunAnalysis(
        simulationFile, simulationTruth, output_dir)
    Analysis.analysis_main()
    wild_card_path = os.path.join(output_dir, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i==2


def test_dummy_delete_files2():
    shutil.rmtree(output_dir)