"""
Call with 'python'

Usage: observations_analysis_main.py --input_dir=DIR --output_dir=DIR [--method=NME]

Options:
    --input_dir=DIR         Directory of the input files
    --output_dir=DIR        Directory of the output files
    --method=NME            [default: both] Name of the method to be used in the analysis (options: amplitude, fuzz or both)
"""

import subprocess
import os.path
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
import docopt
import warnings
warnings.filterwarnings("ignore")

def main():
    try:
        arguments = docopt.docopt(__doc__)
    except docopt.DocoptExit as e:
        print(e)
    print("################ Start fuzziness calculation ################")
    do_calculations(arguments)
    print("################ Finished fuzziness calculation ################")
    print("################ Start fuzziness plotting ################")
    plot(arguments)
    print("################ Finished fuzziness plotting ################")
    print("################ Start distribution analysis ################")
    do_distribution_analysis(arguments)
    print("################ Finished distribution analysis ################")


def do_calculations(arguments):
    input_dir = arguments['--input_dir']
    output_dir = arguments['--output_dir']
    method = arguments['--method']
    filePath = os.path.normpath(os.path.abspath(mrf.__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    amplitude_file_call = os.path.join(parentDir, "scoop_fuzz_amplitude.py")
    fuzz_file_call = os.path.join(parentDir, "scoop_muon_fuzz.py")
    hostfile = os.path.join(parentDir, "scoop_hosts.txt")
    methodList = ["ringM", "hough"]
    for extraction in methodList:
        amplitude_out = os.path.join(output_dir, extraction, "amplitude")
        fuzz_out = os.path.join(output_dir, extraction, "fuzz")
        if method == "amplitude":
            scoopList = [
                "python", "-m", "scoop", "--hostfile",
                hostfile, amplitude_file_call, "--muon_dir",
                input_dir, "--output_dir", amplitude_out,
                "--method", extraction
            ]
            subprocess.call(scoopList)
        elif method == "fuzz":
            scoopList = [
                "python", "-m", "scoop", "--hostfile",
                hostfile, fuzz_file_call, "--muon_dir",
                input_dir, "--output_dir", fuzz_out,
                "--method", extraction
            ]
            subprocess.call(scoopList)
        elif method == "both":
            scoopList_fuzz = [
                "python", "-m", "scoop", "--hostfile",
                hostfile, fuzz_file_call, "--muon_dir",
                input_dir, "--output_dir", fuzz_out,
                "--method", extraction
            ]
            scoopList_amplitude = [
                "python", "-m", "scoop", "--hostfile",
                hostfile, amplitude_file_call, "--muon_dir",
                input_dir, "--output_dir", amplitude_out,
                "--method", extraction
            ]
            subprocess.call(scoopList_fuzz)
            subprocess.call(scoopList_amplitude)


def plot(arguments):
    output_dir = arguments['--output_dir']
    method = arguments['--method']
    filePath = os.path.normpath(os.path.abspath(mrf.__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    filePath = os.path.normpath(os.path.abspath(__file__))
    directory = os.path.normpath(os.path.join(filePath, os.pardir))
    file_call = os.path.join(directory, "merge_fuzz_and_plot_nightwise.py")
    epochFile_path = os.path.join(directory, "epoch_file.csv")
    methodList = ["ringM", "hough"]
    for extraction in methodList:
        amplitude_out = os.path.join(output_dir, extraction, "amplitude")
        fuzz_out = os.path.join(output_dir, extraction, "fuzz")
        plot_out = os.path.join(output_dir, extraction)
        subprocessCall_amplitude = [
            "python", file_call, "--merged_nightwise",
            amplitude_out, "--plot_directory", plot_out,
            "--path_to_epoch_file", epochFile_path,
            "--method", "amplitude"
        ]
        subprocessCall_fuzz = [
            "python", file_call, "--merged_nightwise",
            fuzz_out, "--plot_directory", plot_out,
            "--path_to_epoch_file", epochFile_path,
            "--method", "fuzz"
        ]
        if method == "amplitude":
            subprocess.call(scoopList_amplitude)
        elif method == "fuzz":
            subprocess.call(scoopList_fuzz)
        elif method == "both":
            subprocess.call(subprocessCall_fuzz)
            subprocess.call(subprocessCall_amplitude)
        subprocess.call(["rm", "-r", str(amplitude_out)])
        subprocess.call(["rm", "-r", str(fuzz_out)])


def do_distribution_analysis(arguments):
    input_dir = arguments['--input_dir']
    output_dir = arguments['--output_dir']
    ringM_fileCall = "scoop_real_distributions_ringM.py"
    hough_fileCall = "scoop_real_distributions.py"
    filePath = os.path.normpath(os.path.abspath(mrf.__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    ringM_out = os.path.join(output_dir, "ringM_distribution")
    hostfile = os.path.join(parentDir, "scoop_hosts.txt")
    scoopList_ringM = [
        "python", "-m", "scoop", "--hostfile",
        hostfile, ringM_fileCall, "--muon_dir",
        input_dir, "--output_dir", ringM_out
    ]
    subprocess.call(scoopList_ringM)
    hough_out = os.path.join(output_dir, "hough_distribution")
    scoopList_hough = [
        "python", "-m", "scoop", "--hostfile",
        hostfile, hough_fileCall, "--muon_dir",
        input_dir, "--output_dir", hough_out
    ]
    subprocess.call(scoopList_hough)
    analyze_fileCall = "analyze_method_distribution.py"
    plotOut_dir = os.path.join(output_dir, "distribution_plots")
    analyze_call = [
        "python", analyze_fileCall, "--hough_dir",
        hough_out, "--ringM_dir", ringM_out,
        "--plot_out", plotOut_dir
    ]
    subprocess.call(analyze_call)
    subprocess.call(["rm", "-r", str(ringM_out)])
    subprocess.call(["rm", "-r", str(hough_out)])


if __name__ == "__main__":
    main()