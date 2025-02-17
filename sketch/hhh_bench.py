from collections import defaultdict
from socket import ntohl
from tqdm import tqdm

from utils import read_data, read_labels, and_bytes_int

LAYER1 = 33
MASK = [
    0xffffffff, 0x80000000, 0xc0000000, 0xe0000000, 0xf0000000, 0xf8000000,
    0xfc000000, 0xfe000000, 0xff000000, 0xff800000, 0xffc00000, 0xffe00000,
    0xfff00000, 0xfff80000, 0xfffc0000, 0xfffe0000, 0xffff0000, 0xffff8000,
    0xffffc000, 0xffffe000, 0xfffff000, 0xfffff800, 0xfffffc00, 0xfffffe00,
    0xffffff00, 0xffffff80, 0xffffffc0, 0xffffffe0, 0xfffffff0, 0xfffffff8,
    0xfffffffc, 0xfffffffe, 0x0
]


class HHHBench:

    def __init__(self, dataset_file, label_file):
        self.dataset = read_data(dataset_file)
        self.labels = read_labels(label_file)
        self.mp = [defaultdict(int) for _ in range(LAYER1)]

        for key in self.dataset:
            self.mp[0][key] += 1

        for i in range(1, LAYER1):
            for key, value in self.mp[0].items():
                self.mp[i][and_bytes_int(key, MASK[i])] += value

    def insert(self, sketch, USE_LABEL=False):
        if USE_LABEL:
            for i, key in tqdm(enumerate(self.dataset)):
                sketch.insert(key, self.labels[i])
        else:
            for i, key in tqdm(enumerate(self.dataset)):
                sketch.insert(key)

    def evaluate(self, sketch, alpha):
        estMp = [defaultdict(int) for _ in range(LAYER1)]
        estMp[0] = sketch.all_query()

        for i in range(1, LAYER1):
            for key, value in estMp[0].items():
                estMp[i][and_bytes_int(key, MASK[i])] += value

        threshold = int(alpha * len(self.dataset))

        realHH = estHH = bothHH = aae = are = 0

        for i in range(LAYER1):
            for key, realF in self.mp[i].items():
                estF = estMp[i].get(key, 0)

                real = realF > threshold
                est = estF > threshold

                realHH += real
                estHH += est

                if real and est:
                    bothHH += 1
                    aae += abs(realF - estF)
                    are += abs(realF - estF) / realF

        RR = bothHH / realHH if realHH else 0
        PR = bothHH / estHH if estHH else 0
        F1 = 2 * PR * RR / (PR + RR)

        # print(f"threshold,{threshold}")
        # print(f"realHH,{realHH}")
        # print(f"estHH,{estHH}")
        # print(f"bothHH,{bothHH}")
        # print(f"recall,{RR}")
        # print(f"precision,{PR}")
        print(f"f1,{F1}")
        print(f"aae,{aae / bothHH if bothHH else 0}")
        print(f"are,{are / bothHH if bothHH else 0}")
        print()
