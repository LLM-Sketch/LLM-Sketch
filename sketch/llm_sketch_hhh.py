import random
from collections import defaultdict

from heavy_part import HeavyPart
from coco_sketch import CocoSketch
from utils import hash

FINGERPRINT_SEED = 123123


class LLMSketchHHH:

    def __init__(self, MEMORY, HEAVY_RATIO=0.5):
        self.heavy_part = HeavyPart(MEMORY * HEAVY_RATIO, KEY_LEN=4)
        self.light_part = CocoSketch(MEMORY * (1 - HEAVY_RATIO))

    def insert(self, key, label, inc=1):

        res_key, res_value, res_swap = self.heavy_part.insert(key, label, inc)

        if res_key is not None:
            self.light_part.insert(res_key, res_value)

    def all_query(self):
        res1 = self.heavy_part.all_query()
        res2 = self.light_part.all_query()

        for key, value in res2.items():
            res1[key] += value

        return res1
