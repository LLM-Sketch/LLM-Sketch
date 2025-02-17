# LLM-Sketch: Enhancing Network Sketches with LLM

## Introduction

Network stream mining is fundamental to many network operations. Sketches, as compact data structures that offer low memory overhead with bounded accuracy, have emerged as a promising solution for network stream mining. Recent studies attempt to optimize sketches using machine learning; however, these approaches face the challenges of lacking adaptivity to dynamic networks and incurring high training costs. In this paper, we propose LLM-Sketch, based on the insight that fields beyond the flow IDs in packet headers can also help infer flow sizes. By using a two-tier data structure and separately recording large and small flows, LLM-Sketch improves accuracy while minimizing memory usage. Furthermore, it leverages fine-tuned large language models (LLMs) to reliably estimate flow sizes. We evaluate LLM-Sketch on three representative tasks, and the results demonstrate that LLM-Sketch outperforms state-of-the-art methods by achieving a $7.5\times$ accuracy improvement.

## File Description

- `data/`: Example datasets.
- `model/`: Source code for the flow classifier.
- `sketch/`: Source code for the sketch.

## Environment

- Python dependencies are listed in `environment.yml`.
- For dataset manipulation, you will also need:
  - `cmake`
  - `g++`