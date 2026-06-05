"""
Fine-tune RoBERTa for binary fake news classification.

Usage:
    python -m ml.training.train_roberta [--epochs 3] [--batch_size 16] [--lr 2e-5]
"""
import argparse
import json
import os
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizer,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from ml.training.preprocess import create_dataloaders
from ml.training.download_datasets import prepare_all_datasets

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "roberta-fakenews"
BASE_MODEL = "roberta-base"


def train_epoch(model, dataloader, optimizer, scheduler, device):
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="binary")

    return avg_loss, accuracy, f1


def evaluate(model, dataloader, device):
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            logits = outputs.logits

            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="binary")
    precision = precision_score(all_labels, all_preds, average="binary")
    recall = recall_score(all_labels, all_preds, average="binary")

    return avg_loss, accuracy, f1, precision, recall


def main():
    parser = argparse.ArgumentParser(description="Fine-tune RoBERTa for fake news detection")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max_length", type=int, default=512)
    args = parser.parse_args()

    # Prepare data if not already done
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed"
    if not (data_dir / "train.json").exists():
        print("Datasets not found. Preparing...")
        prepare_all_datasets()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load tokenizer and model
    print(f"Loading {BASE_MODEL}...")
    tokenizer = RobertaTokenizer.from_pretrained(BASE_MODEL)
    model = RobertaForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=2
    ).to(device)

    # Create dataloaders
    train_loader, val_loader, test_loader = create_dataloaders(
        tokenizer, batch_size=args.batch_size, max_length=args.max_length
    )
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}, Test batches: {len(test_loader)}")

    # Optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
    )

    # Training loop
    best_f1 = 0.0
    training_log = []

    for epoch in range(args.epochs):
        print(f"\n--- Epoch {epoch + 1}/{args.epochs} ---")

        train_loss, train_acc, train_f1 = train_epoch(
            model, train_loader, optimizer, scheduler, device
        )
        print(f"Train - Loss: {train_loss:.4f}, Accuracy: {train_acc:.4f}, F1: {train_f1:.4f}")

        val_loss, val_acc, val_f1, val_prec, val_rec = evaluate(model, val_loader, device)
        print(f"Val   - Loss: {val_loss:.4f}, Accuracy: {val_acc:.4f}, F1: {val_f1:.4f}, "
              f"Precision: {val_prec:.4f}, Recall: {val_rec:.4f}")

        epoch_log = {
            "epoch": epoch + 1,
            "train_loss": round(train_loss, 4),
            "train_accuracy": round(train_acc, 4),
            "train_f1": round(train_f1, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_f1": round(val_f1, 4),
            "val_precision": round(val_prec, 4),
            "val_recall": round(val_rec, 4),
        }
        training_log.append(epoch_log)

        # Save best model
        if val_f1 > best_f1:
            best_f1 = val_f1
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(MODEL_DIR))
            tokenizer.save_pretrained(str(MODEL_DIR))
            print(f"  Saved best model (F1: {val_f1:.4f})")

    # Final test evaluation
    print("\n--- Test Evaluation ---")
    test_loss, test_acc, test_f1, test_prec, test_rec = evaluate(model, test_loader, device)
    print(f"Test - Accuracy: {test_acc:.4f}, F1: {test_f1:.4f}, "
          f"Precision: {test_prec:.4f}, Recall: {test_rec:.4f}")

    # Save training log and metrics
    metrics = {
        "training_log": training_log,
        "test_metrics": {
            "accuracy": round(test_acc, 4),
            "f1_score": round(test_f1, 4),
            "precision": round(test_prec, 4),
            "recall": round(test_rec, 4),
        },
        "config": {
            "base_model": BASE_MODEL,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "max_length": args.max_length,
        },
    }

    metrics_path = MODEL_DIR / "training_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
