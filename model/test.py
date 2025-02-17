import torch
from transformers import RobertaForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error
from torch.utils.data import DataLoader
from pathlib import Path
import numpy as np
from peft import PeftModel
from tqdm import tqdm

from packet_tokenizer import PacketTokenizer
from packet_dataset import make_dataset

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vocab = [f"{i:04x}"
         for i in range(65536)] + ["[CLS]", "[SEP]", "[PAD]", "[UNK]"]
tokenizer = PacketTokenizer(vocab)

dataset_dir = "../data/npz/"
test_files = ["1.npz"]
val_dataset = make_dataset(dataset_dir, test_files, tokenizer, shuffle=False)

checkpoint_path = "./lora_results/"
model = RobertaForSequenceClassification.from_pretrained("roberta-base",
                                                         num_labels=1)
model.resize_token_embeddings(len(tokenizer))

model = PeftModel.from_pretrained(model, checkpoint_path)

model.to(device)


def infer_and_analyze(dataset):
    dataloader = DataLoader(dataset, batch_size=64, shuffle=False)
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in tqdm(dataloader):
            input_ids = batch["input_ids"].cuda() if torch.cuda.is_available(
            ) else batch["input_ids"]
            attention_mask = batch["attention_mask"].cuda(
            ) if torch.cuda.is_available() else batch["attention_mask"]
            labels = batch["labels"].cpu().numpy()

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = outputs.logits.squeeze().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels)

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    mse = mean_squared_error(all_labels, all_preds)
    mae = mean_absolute_error(all_labels, all_preds)

    binary_labels = (all_labels >= 0.5).astype(int)
    binary_preds = (all_preds >= 0.5).astype(int)

    acc = accuracy_score(binary_labels, binary_preds)
    precision = precision_score(binary_labels, binary_preds, zero_division=1)
    recall = recall_score(binary_labels, binary_preds, zero_division=1)
    f1 = f1_score(binary_labels, binary_preds)

    metrics = {
        "regression_mse": mse,
        "regression_mae": mae,
        "classification_accuracy": acc,
        "classification_precision": precision,
        "classification_recall": recall,
        "classification_f1": f1
    }

    return metrics, all_preds


metrics, all_labels = infer_and_analyze(val_dataset)

print("Metrics:", metrics)

output_labels_path = Path("pred/" + test_files[0])
np.savez(output_labels_path, labels=all_labels)
print(f"Labels saved to {output_labels_path}")
