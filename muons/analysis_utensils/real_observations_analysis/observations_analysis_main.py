"""
Call with 'python'

Usage: observations_analysis_main.py --input_dir=DIR --output_dir=DIR --method=NME

Options:
    --input_dir=DIR         Directory of the input files
    --output_dir=DIR        Directory of the output files
    --method=NME            Name of the method to be used in the analysis (options: amplitude, fuzz or both)
"""

import subprocess
import os.path
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
import docopt


def main():
    try:
        arguments = docopt.docopt(__doc__)
    except docopt.DocoptExit as e:
        print(e)
    do_calculations(arguments)
    plot(arguments)
    do_distribution_analysis(arguments)



def do_calculations(arguments):
    input_dir = arguments['--input_dir']
    output_dir = arguments['--output_dir']
    method = arguments['--method']
    filePath = os.path.normpath(os.path.abspath(mrf.__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    amplitude_file_call = os.path.join(parentDir, "scoop_fuzz_amplitude.py")
    amplitude_out = os.path.join(output_dir, "amplitude")
    fuzz_file_call = os.path.join(parentDir, "scoop_muon_fuzz.py")
    fuzz_out = os.path.join(output_dir, "fuzz")
    hostfile = os.path.join(parentDir, "scoop_hosts.txt")
    if method == "amplitude":
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            hostfile, amplitude_file_call, "--muon_dir",
            input_dir, "--output_dir", amplitude_out
        ]
        subprocess.call(scoopList)
    elif method == "fuzz":
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            hostfile, fuzz_file_call, "--muon_dir",
            input_dir, "--output_dir", fuzz_out
        ]
        subprocess.call(scoopList)
    elif method == "both":
        scoopList_fuzz = [
            "python", "-m", "scoop", "--hostfile",
            hostfile, fuzz_file_call, "--muon_dir",
            input_dir, "--output_dir", amplitude_out
        ]
        scoopList_amplitude = [
            "python", "-m", "scoop", "--hostfile",
            hostfile, amplitude_file_call, "--muon_dir",
            input_dir, "--output_dir", fuzz_out
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
    amplitude_dir = os.path.join(output_dir, "amplitude")
    fuzz_dir = os.path.join(output_dir, "fuzz")
    file_call = os.path.join(directory, "merge_fuzz_and_plot_nightwise.py")
    epochFile_path = os.path.join(directory, "epoch_file.csv")
    hostfile = os.path.join(parentDir, "scoop_hosts.txt")
    #kas peab veel enne seda kõik mergema nightwise?? või võib kohe kasutada seda?
    scoopList_amplitude = [
        "python", "-m", "scoop", "--hostfile",
        hostfile, file_call, "--merged_nightwise",
        amplitude_dir, "--plot_directory", output_dir,
        "--path_to_epoch_file", epochFile_path
    ]
    scoopList_fuzz = [
        "python", "-m", "scoop", "--hostfile",
        hostfile, file_call, "--merged_nightwise",
        fuzz_dir, "--plot_directory", output_dir,
        "--path_to_epoch_file", epochFile_path
    ]
    if method == "amplitude":
        subprocess.call(scoopList_amplitude)
    elif method == "fuzz":
        subprocess.call(scoopList_fuzz)
    elif method == "both":
        subprocess.call(scoopList_amplitude)
        subprocess.call(scoopList_fuzz)


def do_distribution_analysis(arguments):
    input_dir = arguments['--input_dir']
    output_dir = argument['--output_dir']
    ringM_fileCall = "scoop_real_distributions_ringM.py"
    hough_fileCall = "scoop_real_distributions.py"
    ringM_out = os.path.join(output_dir, "ringM_distribution")
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
    analyze_fileCall = os.path.join(output_dir, "analyze_method_distribution.py")
    plotOut_dir = os.path.join(output_dir, "Plots")
    scoopList_analyze = [
        "python", "-m", "scoop", "--hostfile",
        hostfile, analyze_fileCall, "--hough_dir",
        hough_out, "--ringM_dir", ringM_out,
        "--plot_out", plotOut_dir
    ]



if __name__ == "__main__":
    main()