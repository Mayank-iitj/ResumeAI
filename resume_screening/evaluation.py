from typing import Dict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


def evaluate_fit(y_true, y_pred, y_prob=None) -> Dict[str, float]:
    """Compute evaluation metrics for candidate fit predictions.

    y_true: list/array of ground truth labels (0/1)
    y_pred: list/array of predicted labels (0/1)
    y_prob: optional list/array of predicted probabilities for positive class
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
        except Exception:
            metrics["roc_auc"] = 0.0
    return metrics
