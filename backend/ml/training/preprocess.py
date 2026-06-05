"""
Text preprocessing utilities for fake news detection.
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

import torch
from torch.utils.data import Dataset
from transformers import RobertaTokenizer

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed"


def clean_text(text: str) -> str:
    """Clean and normalize text for model input."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove excessive punctuation but keep some for style detection
    text = re.sub(r"([!?.]){4,}", r"\1\1\1", text)
    return text


class FakeNewsDataset(Dataset):
    """PyTorch Dataset for fake news classification."""

    def __init__(
        self,
        data: List[Dict],
        tokenizer: RobertaTokenizer,
        max_length: int = 512,
    ):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = clean_text(item["text"])
        label = item["label"]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
        }


def load_split(split: str) -> List[Dict]:
    """Load a data split from processed JSON."""
    path = DATA_DIR / f"{split}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Data split '{split}' not found at {path}. "
            "Run download_datasets.py first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_dataloaders(
    tokenizer: RobertaTokenizer,
    batch_size: int = 16,
    max_length: int = 512,
) -> Tuple[torch.utils.data.DataLoader, torch.utils.data.DataLoader, torch.utils.data.DataLoader]:
    """Create train, validation, and test dataloaders."""
    train_data = load_split("train")
    val_data = load_split("val")
    test_data = load_split("test")

    train_dataset = FakeNewsDataset(train_data, tokenizer, max_length)
    val_dataset = FakeNewsDataset(val_data, tokenizer, max_length)
    test_dataset = FakeNewsDataset(test_data, tokenizer, max_length)

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=0
    )
    val_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )

    return train_loader, val_loader, test_loader
