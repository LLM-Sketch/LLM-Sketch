You can train and test the model using the following commands:

```
python3 train.py
mkdir pred
python3 test.py
```

### Customizing the Dataset

To use your own datasets, modify the following lines in the code:

- `train.py`: Lines 25–27 (`dataset_dir`, `train_files`, `test_files`)
- `test.py`: Lines 19–20 (`dataset_dir`, `test_files`)

Make sure these paths correspond to the directories and files where your dataset is located. This will ensure that both training and testing scripts can correctly load and process your data.