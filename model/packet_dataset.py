import numpy as np
import torch
from torch.utils.data import Dataset
from scipy.special import expit

a = 2.298
pivot = 6


class PacketDataset(Dataset):

    def __init__(self, packets, labels, tokenizer, max_length):
        self.packets = packets
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.packets)

    def __getitem__(self, idx):
        packet = self.packets[idx]
        label = self.labels[idx]
        encoding = self.tokenizer.encode(packet)
        input_ids = torch.tensor(encoding, dtype=torch.long)
        attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': torch.tensor(label, dtype=torch.float)
        }


def make_dataset(dir,
                 files,
                 tokenizer,
                 threshold=None,
                 max_length=40,
                 shuffle=True):
    all_packets = []
    all_flow_sizes = []

    for file in files:
        file_path = dir + file
        print(f"Loading {file_path}...")
        data = np.load(file_path, allow_pickle=True)
        headers = data['header']
        flow_sizes = data['flow_size']

        if threshold:
            headers = headers[:threshold]
            flow_sizes = flow_sizes[:threshold]

        all_packets.append(headers)
        all_flow_sizes.append(flow_sizes)

    all_packets = np.concatenate(all_packets, axis=0)
    all_flow_sizes = np.concatenate(all_flow_sizes, axis=0)

    if threshold:
        all_packets = all_packets[:threshold]
        all_flow_sizes = all_flow_sizes[:threshold]

    all_labels = expit(a * (np.log2(all_flow_sizes) - pivot))

    if shuffle:
        combined = list(zip(all_packets, all_labels))
        np.random.shuffle(combined)
        all_packets, all_labels = zip(*combined)

    return PacketDataset(all_packets, all_labels, tokenizer, max_length)
