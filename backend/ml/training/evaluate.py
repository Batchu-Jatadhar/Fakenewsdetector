"""
Evaluate trained models on the test set.

Usage:
    python -m ml.training.evaluate
"""
import json
from pathlib import Path

import torch
import numpy as np
from transformers import RobertaForSequenceClassification, RobertaTokenizer
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix,
)

from ml.training.preprocess import load_split, clean_text

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "roberta-fakenews"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "models" / "evaluation"


def evaluate_roberta():
    """Evaluate the fine-tuned RoBERTa model on the test set."""
    print("=== Evaluating RoBERTa Classifier ===")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not MODEL_DIR.exists():
        print(f"Model not found at {MODEL_DIR}. Train first with train_roberta.py")
        return None

    tokenizer = RobertaTokenizer.from_pretrained(str(MODEL_DIR))
    model = RobertaForSequenceClassification.from_pretrained(str(MODEL_DIR)).to(device)
    model.eval()

    test_data = load_split("test")
    print(f"Test samples: {len(test_data)}")

    all_preds = []
    all_labels = []
    all_probs = []

    batch_size = 32
    for i in range(0, len(test_data), batch_size):
        batch = test_data[i:i + batch_size]
        texts = [clean_text(item["text"]) for item in batch]
        labels = [item["label"] for item in batch]

        encoding = tokenizer(
            texts, max_length=512, padding=True, truncation=True, return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            outputs = model(**encoding)
            probs = torch.softmax(outputs.logits, dim=1)
            preds = torch.argmax(probs, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels)
        all_probs.extend(probs[:, 1].cpu().numpy())  # P(fake)

    # Compute metrics
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="binary")
    precision = precision_score(all_labels, all_preds, average="binary")
    recall = recall_score(all_labels, all_preds, average="binary")

    print(f"\nAccuracy:  {accuracy:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=["Real", "Fake"]))
    print(f"Confusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))

    results = {
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "total_samples": len(test_data),
        "confusion_matrix": confusion_matrix(all_labels, all_preds).tolist(),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / "test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {RESULTS_DIR / 'test_results.json'}")
    return results


if __name__ == "__main__":
    evaluate_roberta()
