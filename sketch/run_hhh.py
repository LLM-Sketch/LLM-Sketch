from hhh_bench import HHHBench
from llm_sketch_hhh import LLMSketchHHH

dataset_file = "../data/npz/1.npz"
label_file = "../model/pred/1.npz"


def main():
    bench = HHHBench(dataset_file, label_file)

    for i in range(50, 300, 50):
        memory_size = i * 1024

        ours = LLMSketchHHH(memory_size, HEAVY_RATIO=0.5)
        bench.insert(ours, USE_LABEL=True)

        print(f"Memory = {i}KB")
        bench.evaluate(ours, 0.0001)


if __name__ == "__main__":
    main()
