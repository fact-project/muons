import numpy as np
import photon_stream as ps
from muons.analysis_utensils.advanced_detection import detection
import os


def test_muon_detection():

    np.random.seed(seed=1)

    muon_sample_dir = os.path.dirname(os.path.realpath(__file__))
    muon_truth_path = os.path.join(
        muon_sample_dir, 'resources', 'muon_sample_20140101_104.csv')

    muon_truth = np.genfromtxt(muon_truth_path)

    muon_sample_path = os.path.join(
        muon_sample_dir, 'resources', '20140101_104_muon_sample.phs.jsonl.gz')


    run = ps.EventListReader(muon_sample_path)

    true_positives = 0
    true_negatives = 0

    false_positives = 0
    false_negatives = 0

    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        ret = detection(event, clusters)
        
        if ret['is_muon']:
            if event.observation_info.event in muon_truth:
                true_positives += 1
            else:
                false_positives += 1
        else:
            if event.observation_info.event in muon_truth:
                false_negatives += 1
            else:
                true_negatives += 1

    precision = true_positives / (true_positives + false_positives)
    sensitivity = true_positives / (true_positives + false_negatives)

    print('precision', precision)
    print('sensitivity', sensitivity)

    assert precision > 0.995
    assert sensitivity > 0.76