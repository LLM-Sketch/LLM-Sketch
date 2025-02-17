import random
from collections import defaultdict

from utils import Counter, hash


class HeavyPart:

    def __init__(self, MEMORY, BUCKET_SIZE=8, KEY_LEN=13, COUNTER_LEN=4):
        self.NUM_BUCKETS = int(MEMORY / BUCKET_SIZE / (KEY_LEN + COUNTER_LEN))
        self.BUCKET_SIZE = BUCKET_SIZE
        self.counter = [[Counter() for _ in range(BUCKET_SIZE)]
                        for _ in range(self.NUM_BUCKETS)]

    def insert(self, key, label, inc=1):
        position = hash(key) % self.NUM_BUCKETS
        bucket = self.counter[position]

        min_idx, min_key, min_value = None, None, float('inf')

        for i in range(self.BUCKET_SIZE):
            if bucket[i].ID == key:
                bucket[i].count += 1
                bucket[i].flag = random.random() < (bucket[i].flag *
                                                    (bucket[i].count - 1) +
                                                    label) / bucket[i].count
                return None, None, None

            if bucket[i].ID is None:
                bucket[i].ID, bucket[i].count = key, inc
                bucket[i].flag = label >= 0.5
                return None, None, None

            if bucket[i].flag is False and bucket[i].count < min_value:
                min_idx, min_key, min_value = i, bucket[i].ID, bucket[i].count

        if label < 0.5:
            return key, inc, False

        if min_idx is None:
            for i in range(self.BUCKET_SIZE):
                if bucket[i].count < min_value:
                    min_idx, min_key, min_value = i, bucket[i].ID, bucket[
                        i].count

        bucket[min_idx].ID, bucket[min_idx].count = key, inc
        bucket[min_idx].flag = True

        return min_key, min_value, True

    def query(self, key):
        position = hash(key) % self.NUM_BUCKETS
        bucket = self.counter[position]

        for i in range(self.BUCKET_SIZE):
            if bucket[i].ID == key:
                return bucket[i].count

    def all_query(self):
        ret = defaultdict(int)

        for i in range(self.NUM_BUCKETS):
            for j in range(self.BUCKET_SIZE):
                if self.counter[i][j].ID is not None:
                    ret[self.counter[i][j].ID] = self.counter[i][j].count

        return ret
