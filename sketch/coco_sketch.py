import random
from collections import defaultdict

from utils import Counter, hash


class CocoSketch:

    def __init__(self, MEMORY, HASH_NUM=2, KEY_LEN=4):
        self.HASH_NUM = HASH_NUM
        self.LENGTH = int(MEMORY / HASH_NUM / (KEY_LEN + 4))

        self.counter = [[Counter() for _ in range(self.LENGTH)]
                        for _ in range(HASH_NUM)]

    def insert(self, item, inc=1):
        minimum = float('inf')
        min_pos = None
        min_hash = None

        for i in range(self.HASH_NUM):
            position = hash(item, i) % self.LENGTH
            if self.counter[i][position].ID == item:
                self.counter[i][position].count += inc
                return
            if self.counter[i][position].count < minimum:
                min_pos = position
                min_hash = i
                minimum = self.counter[i][position].count

        self.counter[min_hash][min_pos].count += 1
        if random.randint(0, self.counter[min_hash][min_pos].count - 1) == 0:
            self.counter[min_hash][min_pos].ID = item

    def all_query(self):
        ret = defaultdict(int)

        for i in range(self.HASH_NUM):
            for j in range(self.LENGTH):
                if self.counter[i][j].ID is not None:
                    ret[self.counter[i][j].ID] = self.counter[i][j].count

        return ret
