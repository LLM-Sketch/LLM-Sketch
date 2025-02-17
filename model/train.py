import numpy as np
import torch
from transformers import RobertaForSequenceClassification, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from sklearn.metrics import mean_squared_error, mean_absolute_error

from packet_tokenizer import PacketTokenizer
from packet_dataset import make_dataset


def compute_metrics(pred):
    predictions, labels = pred.predictions, pred.label_ids
    preds = predictions.squeeze()
    mse = mean_squared_error(labels, preds)
    mae = mean_absolute_error(labels, preds)
    return {"eval_mse": mse, "eval_mae": mae}


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vocab = [f"{i:04x}"
         for i in range(65536)] + ["[CLS]", "[SEP]", "[PAD]", "[UNK]"]
tokenizer = PacketTokenizer(vocab)

dataset_dir = "../data/npz/"
train_files = ["0.npz"]
test_files = ["1.npz"]

train_dataset = make_dataset(dataset_dir, train_files, tokenizer)
val_dataset = make_dataset(dataset_dir,
                           test_files,
                           tokenizer,
                           threshold=100000)

model = RobertaForSequenceClassification.from_pretrained("roberta-base",
                                                         num_labels=1)
model.resize_token_embeddings(len(tokenizer))

for name, param in model.named_parameters():
    if "embeddings" in name:
        param.requires_grad = True

lora_config = LoraConfig(task_type=TaskType.SEQ_CLS,
                         target_modules=["query", "key", "value"],
                         inference_mode=False,
                         r=8,
                         lora_alpha=32,
                         lora_dropout=0.1)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

model.to(device)

training_args = TrainingArguments(run_name="bert-sketch",
                                  output_dir="./lora_results",
                                  logging_dir="./lora_logs",
                                  eval_strategy="steps",
                                  save_total_limit=5,
                                  eval_steps=4000,
                                  save_steps=16000,
                                  load_best_model_at_end=True,
                                  learning_rate=2e-5,
                                  per_device_train_batch_size=64,
                                  per_device_eval_batch_size=64,
                                  num_train_epochs=1,
                                  weight_decay=0.01,
                                  dataloader_num_workers=5,
                                  fp16=True,
                                  metric_for_best_model="eval_mse")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

trainer.save_state()
trainer.save_model(output_dir=training_args.output_dir)
