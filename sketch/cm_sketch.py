from utils import hash


class CMSketch:

    def __init__(self, MEMORY, HASH_NUM=3, COUNTER_LEN=4):
        self.HASH_NUM = HASH_NUM
        self.COUNTER_MAX = 256**COUNTER_LEN - 1
        self.LENGTH = int(MEMORY / HASH_NUM / COUNTER_LEN)

        self.counter = [[0 for _ in range(self.LENGTH)]
                        for _ in range(HASH_NUM)]

        self.overflow_count = 0

    def insert(self, item, inc=1):
        for i in range(self.HASH_NUM):
            pos = hash(item, i) % self.LENGTH
            self.counter[i][pos] += inc
            if self.counter[i][pos] > self.COUNTER_MAX:
                self.counter[i][pos] = self.COUNTER_MAX
                self.overflow_count += 1

    def swap_insert(self, item, value):
        value = min(value, self.COUNTER_MAX)
        for i in range(self.HASH_NUM):
            pos = hash(item, i) % self.LENGTH
            self.counter[i][pos] = max(self.counter[i][pos], value)

    def query(self, item):
        ret = float('inf')

        for i in range(self.HASH_NUM):
            position = hash(item, i) % self.LENGTH
            ret = min(ret, self.counter[i][position])

        return ret
