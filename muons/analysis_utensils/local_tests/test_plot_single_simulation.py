import sys
import os
import shutil
import glob
from muons.analysis_utensils.simulation_analysis import(
    plot_single_simulation as pss)
import pandas



filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
reconstructed_muons_path = os.path.join(
    fileDir, "resources", "reconstructed_muons.csv")
simulationTruth = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.simulationtruth.csv")
output_dir = os.path.join(fileDir, "resources", "testDir")


def test_check_inputValidity():
    try:
        Ssp = pss.SingleSimulatonPlotting(
            reconstructed_muons_path, simulationTruth, output_dir)
        Ssp.check_inputValidity()
        error = False
    except ValueError:
        error = True
    assert error == False


def test_check_inputValidity_wrong_reconstructedPath():
    try:
        Ssp = pss.SingleSimulatonPlotting(
            "/foo/bar", simulationTruth, output_dir)
        Ssp.check_inputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_inputValidity_wrong_simTruth():
    try:
        Ssp = pss.SingleSimulatonPlotting(
            reconstructed_muons_path, "/foo/bar", output_dir)
        Ssp.check_inputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True



def test_check_inputValidity_wrong_outputDir():
    try:
        Ssp = pss.SingleSimulatonPlotting(
            reconstructed_muons_path, simulationTruth, 3)
        Ssp.check_inputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_create_outputDir():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.create_outputDir()
    existing = False
    if os.path.isdir(output_dir):
        existing = True
    assert existing == True


def test_create_bins():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    input_data = [1, 2, 3, 4]
    bin_edges = Ssp.create_bins(input_data)
    assert (bin_edges == [1, 2.5, 4]).all()


def test_read_dataFrames_simulationTruth():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    simulation_truth, extracted_muons = Ssp.read_dataframes()
    assert len(simulation_truth.keys()) == 16


def test_read_dataFrames_extractedMuons():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    simulation_truth, extracted_muons = Ssp.read_dataframes()
    assert (
        len(extracted_muons.keys()) == 7 or len(extracted_muons.keys()) == 4)


def test_choose_muon_events():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    muEvents = Ssp.choose_muon_events()
    assert (muEvents == [3, 8, 14, 16, 28, 36, 43, 61, 74, 97]).all()


def test_create_axis():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    fig, ax = Ssp.create_axis()
    existing = False
    if not (fig == None or ax==None):
        existing = True
    assert existing == True


def test_plot_plot_gaussDistribution_for_R_width():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.plot_gaussDistribution_for_R_width()
    path = os.path.join(output_dir, "r_difference_gauss.png")
    existing = False
    if os.path.exists(path):
        existing = True
    assert existing == True


def test_calculate_r_sq():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    r_d_sq, r_t_sq = Ssp.calculate_r_sq()
    assert (len(r_d_sq) == 10 and len(r_t_sq) == 100)


def test_plot_impact_r_sq():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.plot_impact_r_sq()
    path = os.path.join(output_dir, "impact_r_sq.png")
    existing = False
    if os.path.exists(path):
        existing = True
    assert existing == True


def test_extract_cx_cy_returnsAll():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    returns = Ssp.extract_cx_cy()
    assert len(returns) == 6


def test_extract_cx_cy_returnsThrown():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    returns = Ssp.extract_cx_cy()
    assert len(returns[0]) == 100


def test_extract_cx_cy_returnsDetected():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    returns = Ssp.extract_cx_cy()
    assert len(returns[2]) == 10 and len(returns[3]) == 10


def test_extract_cx_cy_returnsReconstructed():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    returns = Ssp.extract_cx_cy()
    assert len(returns[4]) == 10 and len(returns[5]) == 10


def test_plot_cxcy_sq():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.plot_cxcy_sq()
    path = os.path.join(output_dir, "cxcy_squared.png")
    existing = False
    if os.path.exists(path):
        existing = True
    assert existing == True


def test_plot_cx_reconstructed_and_thrown():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.plot_cx_reconstructed_and_thrown()
    plotPath = os.path.join(output_dir, "confusionMatrix_cx.png")
    existing = False
    if os.path.exists(plotPath):
        existing = True
    assert existing == True


def test_plot_cy_reconstructed_and_thrown():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.plot_cy_reconstructed_and_thrown()
    plotPath = os.path.join(output_dir, "confusionMatrix_cy.png")
    existing = False
    if os.path.exists(plotPath):
        existing = True
    assert existing == True


def test_confusionMatrix_opening_angle():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.confusionMatrix_opening_angle()
    plotPath = os.path.join(output_dir, "confusionMatrix_oa.png")
    existing = False
    if os.path.exists(plotPath):
        existing = True
    assert existing == True


def test_compare_thrown_muon_opening_angle_with_detected():
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, output_dir)
    Ssp.compare_thrown_muon_opening_angle_with_detected()
    plotPath = os.path.join(output_dir, "opening_angle.png")
    existing = False
    if os.path.exists(plotPath):
        existing = True
    assert existing == True


def test_create_all_singleSimulation_plots():
    mainOut = os.path.join(output_dir, "main")
    Ssp = pss.SingleSimulatonPlotting(
        reconstructed_muons_path, simulationTruth, mainOut)
    Ssp.create_all_singleSimulation_plots()
    wild_card_path = os.path.join(mainOut, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 7


def test_dummy_delete_files():
    shutil.rmtree(output_dir)
