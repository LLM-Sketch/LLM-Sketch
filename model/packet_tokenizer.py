from transformers import PreTrainedTokenizer


class PacketTokenizer(PreTrainedTokenizer):

    def __init__(self, vocab, max_length=40):
        self.vocab = vocab
        self.token2id = {token: idx for idx, token in enumerate(vocab)}
        self.id2token = {idx: token for token, idx in self.token2id.items()}
        self.max_length = max_length
        super().__init__()

    def get_vocab(self):
        return self.token2id

    def _tokenize(self, packet):
        return [
            f"{packet[i]:02x}{packet[i+1]:02x}"
            for i in range(0, len(packet), 2)
        ]

    def _convert_token_to_id(self, token):
        return self.token2id.get(token, self.token2id["[UNK]"])

    def _convert_id_to_token(self, index):
        return self.id2token.get(index, "[UNK]")

    def encode(self, packet, add_special_tokens=True):
        tokens = self._tokenize(packet)
        token_ids = [self._convert_token_to_id(token) for token in tokens]

        if add_special_tokens:
            cls_id = self.token2id["[CLS]"]
            sep_id = self.token2id["[SEP]"]
            token_ids = [cls_id] + token_ids + [sep_id]

        max_token_id = max(self.token2id.values())

        padding_length = max(0, self.max_length - len(token_ids))
        token_ids = token_ids + [self.token2id["[PAD]"]] * padding_length

        return token_ids

    def decode(self, token_ids, skip_special_tokens=True):
        tokens = [self._convert_id_to_token(idx) for idx in token_ids]
        if skip_special_tokens:
            tokens = [
                token for token in tokens
                if token not in ["[CLS]", "[SEP]", "[PAD]"]
            ]
        return tokens
