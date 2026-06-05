"""
RoBERTa-based fake news classifier inference wrapper.
Loads the fine-tuned model and provides prediction interface.
"""
import torch
from pathlib import Path
from typing import Dict, Optional
from transformers import RobertaForSequenceClassification, RobertaTokenizer

from ml.training.preprocess import clean_text

MODEL_DIR = Path(__file__).resolve().parent / "models" / "roberta-fakenews"
BASE_MODEL = "roberta-base"


class RoBERTaClassifier:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False

    def load(self):
        """Load the fine-tuned model or fall back to base model."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if MODEL_DIR.exists() and (MODEL_DIR / "config.json").exists():
            print(f"Loading fine-tuned model from {MODEL_DIR}")
            self.tokenizer = RobertaTokenizer.from_pretrained(str(MODEL_DIR))
            self.model = RobertaForSequenceClassification.from_pretrained(str(MODEL_DIR)).to(self.device)
        else:
            print(f"Fine-tuned model not found. Loading base model {BASE_MODEL}")
            self.tokenizer = RobertaTokenizer.from_pretrained(BASE_MODEL)
            self.model = RobertaForSequenceClassification.from_pretrained(
                BASE_MODEL, num_labels=2
            ).to(self.device)

        self.model.eval()
        self._loaded = True

    def predict(self, text: str) -> Dict:
        """
        Predict fake news probability for given text.

        Returns:
            {
                "fake_prob": float (0-1, probability of being fake),
                "confidence": float (0-1, model confidence in its prediction),
                "predicted_label": str ("fake" or "real"),
            }
        """
        if not self._loaded:
            self.load()

        cleaned = clean_text(text)

        encoding = self.tokenizer(
            cleaned,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoding)
            probs = torch.softmax(outputs.logits, dim=1)

        fake_prob = probs[0][1].item()  # P(fake)
        real_prob = probs[0][0].item()  # P(real)
        confidence = max(fake_prob, real_prob)  # Confidence is max probability
        predicted_label = "fake" if fake_prob > 0.5 else "real"

        return {
            "fake_prob": round(fake_prob, 4),
            "confidence": round(confidence, 4),
            "predicted_label": predicted_label,
        }

    def get_attention_weights(self, text: str) -> Optional[Dict]:
        """Get attention weights for explainability."""
        if not self._loaded:
            self.load()

        cleaned = clean_text(text)
        encoding = self.tokenizer(
            cleaned,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoding, output_attentions=True)

        # Average attention across all heads of the last layer
        last_layer_attention = outputs.attentions[-1]  # [1, heads, seq, seq]
        avg_attention = last_layer_attention.mean(dim=1).squeeze(0)  # [seq, seq]

        # CLS token attention to all other tokens
        cls_attention = avg_attention[0].cpu().numpy()

        # Get tokens
        tokens = self.tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])
        attention_mask = encoding["attention_mask"][0].cpu().numpy()

        # Filter padding
        token_attention_pairs = [
            (tok, float(att))
            for tok, att, mask in zip(tokens, cls_attention, attention_mask)
            if mask == 1 and tok not in ["<s>", "</s>", "<pad>"]
        ]

        return {
            "token_attentions": token_attention_pairs,
        }


# Singleton instance
_classifier = None


def get_classifier() -> RoBERTaClassifier:
    global _classifier
    if _classifier is None:
        _classifier = RoBERTaClassifier()
        _classifier.load()
    return _classifier
