from benchmark import Benchmark
from llm_sketch import LLMSketch

dataset_file = "../data/npz/1.npz"
label_file = "../model/pred/1.npz"


def main():
    bench = Benchmark(dataset_file, label_file)

    for i in range(200, 1200, 200):
        memory_size = i * 1024

        ours = LLMSketch(memory_size, HEAVY_RATIO=0.2, USING_FINGERPRINT=True)
        bench.insert(ours)

        print(f"Memory = {i}KB")

        AAE, ARE = bench.evaluate_flow_size(ours)
        print(f"AAE = {AAE}, ARE = {ARE}")


if __name__ == "__main__":
    main()
