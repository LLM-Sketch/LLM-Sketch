This folder provides scripts to perform different query types—flow size queries, heavy hitter queries, and 1D-HHH queries—using the sketch-based approach.

### Running Flow Size and Heavy Hitter Queries

Use the following commands to run flow size and heavy hitter queries:

```
python3 run_flow_size.py
python3 run_heavy_hitter.py
```

### Running 1D-HHH Queries

For 1D-HHH queries, you first need to generate a dataset where `srcIP` is used as the key and train a dedicated model on that dataset. Once trained, run:

```
python3 run_hhh.py
```

### Customizing the Datasets

To use your own datasets, modify the `dataset_file` and `label_file` parameters in:

- `run_flow_size.py`
- `run_heavy_hitter.py`
- `run_hhh.py`

You can also adjust other parameters in these scripts (e.g., hyperparameters or thresholds) to suit your data and experiment needs.
