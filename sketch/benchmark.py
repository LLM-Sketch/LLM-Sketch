from collections import defaultdict
from tqdm import tqdm

from utils import read_data, read_labels


class Benchmark:

    def __init__(self, dataset_file, label_file):
        self.dataset = read_data(dataset_file)
        self.labels = read_labels(label_file)
        self.ground_truth = defaultdict(int)

        for key in self.dataset:
            self.ground_truth[key] += 1

    def insert(self, sketch):
        for i, key in tqdm(enumerate(self.dataset)):
            sketch.insert(key, self.labels[i])

    def evaluate_flow_size(self, sketch):

        AAE = sum([
            abs(sketch.query(key) - real)
            for key, real in self.ground_truth.items()
        ]) / len(self.ground_truth)
        ARE = sum([
            abs(sketch.query(key) - real) / real
            for key, real in self.ground_truth.items()
        ]) / len(self.ground_truth)

        return AAE, ARE

    def evaluate_heavy_hitter(self, sketch, alpha):
        est_dict = sketch.all_query()

        threshold = int(alpha * len(self.dataset))

        real_HH = {
            key: value
            for key, value in self.ground_truth.items() if value > threshold
        }
        est_HH = {
            key: value
            for key, value in est_dict.items() if value > threshold
        }

        TP = set(real_HH.keys()) & set(est_HH.keys())
        FP = set(est_HH.keys()) - set(real_HH.keys())
        FN = set(real_HH.keys()) - set(est_HH.keys())

        PR = len(TP) / (len(TP) + len(FP))
        RR = len(TP) / (len(TP) + len(FN))
        F1 = 2 * PR * RR / (PR + RR)

        AAE = sum([abs(est_HH[k] - real_HH[k]) for k in TP]) / len(TP)
        ARE = sum([abs(est_HH[k] - real_HH[k]) / real_HH[k]
                   for k in TP]) / len(TP)

        return F1, AAE, ARE
