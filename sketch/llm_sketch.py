import random
from collections import defaultdict

from heavy_part import HeavyPart
from cm_sketch import CMSketch
from utils import hash

FINGERPRINT_SEED = 123123


class LLMSketch:

    def __init__(self, MEMORY, HEAVY_RATIO=0.5, USING_FINGERPRINT=False):
        if USING_FINGERPRINT:
            self.heavy_part = HeavyPart(MEMORY * HEAVY_RATIO, KEY_LEN=4)
        else:
            self.heavy_part = HeavyPart(MEMORY * HEAVY_RATIO)
        if HEAVY_RATIO < 1:
            self.light_part = CMSketch(MEMORY * (1 - HEAVY_RATIO),
                                       COUNTER_LEN=1)
        else:
            self.light_part = None
        self.using_fingerprint = USING_FINGERPRINT

    def insert(self, key, label, inc=1):
        if self.using_fingerprint:
            key = hash(key, FINGERPRINT_SEED).to_bytes(4, byteorder='little')

        res_key, res_value, res_swap = self.heavy_part.insert(key, label, inc)

        if res_key is not None and self.light_part is not None:
            if res_swap:
                self.light_part.swap_insert(res_key, res_value)
            else:
                self.light_part.insert(res_key, res_value)

    def query(self, key):
        if self.using_fingerprint:
            key = hash(key, FINGERPRINT_SEED).to_bytes(4, byteorder='little')

        res1 = self.heavy_part.query(key)
        if res1 is not None:
            return res1

        if self.light_part is None:
            return 0
        return self.light_part.query(key)

    def all_query(self):
        return self.heavy_part.all_query()
