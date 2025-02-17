import numpy as np
import mmh3


def read_data(file):
    data = np.load(file, allow_pickle=True)
    return data["id"]


def read_labels(file):
    data = np.load(file)
    return data["labels"]


def hash(key, seed=100):
    return mmh3.hash(key, signed=False, seed=seed)


def and_bytes_int(a: bytes, b: int) -> bytes:
    n = len(a)
    b_bytes = b.to_bytes(n, byteorder='little', signed=False)
    return bytes(x & y for x, y in zip(a, b_bytes))


class Counter:

    def __init__(self, ID=None, count=0, flag=False):
        self.ID = ID
        self.count = count
        self.flag = flag
