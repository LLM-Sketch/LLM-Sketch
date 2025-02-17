from benchmark import Benchmark
from llm_sketch import LLMSketch

dataset_file = "../data/npz/1.npz"
label_file = "../model/pred/1.npz"


def main():
    bench = Benchmark(dataset_file, label_file)

    for i in range(50, 300, 50):
        memory_size = i * 1024

        ours = LLMSketch(memory_size, HEAVY_RATIO=1)
        bench.insert(ours)

        print(f"Memory = {i}KB")

        F1, AAE, ARE = bench.evaluate_heavy_hitter(ours, 0.0001)
        print(f"F1 = {F1}, AAE = {AAE}, ARE = {ARE}")


if __name__ == "__main__":
    main()
