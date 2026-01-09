
"""
Train and evaluate multiple classic text classifiers on SMS Spam dataset.
Produces:
- train/metrics_heatmap.png (comparison heatmap)
- app/vectorizer.pkl
- app/model.pkl  (best model by F1)
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt

def load_data(train_dir: Path) -> pd.DataFrame:
    csv_main = train_dir / "sms_spam.csv"
    csv_sample = train_dir / "sms_spam_sample.csv"
    if csv_main.exists():
        df = pd.read_csv(csv_main)
        print(f"Loaded {len(df):,} rows from {csv_main}")
        return df
    print("sms_spam.csv not found. Using small fallback sample dataset.")
    df = pd.read_csv(csv_sample)
    print(f"Loaded {len(df):,} rows from {csv_sample}")
    return df

def clean_text(s: str) -> str:
    # Keep this light to avoid mismatch between training & inference
    return str(s).strip()

def evaluate_model(name: str, model, X_train, X_test, y_train, y_test) -> dict:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, pred, average="binary", pos_label="spam", zero_division=0
    )
    return {"model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "estimator": model}

def plot_heatmap(df_metrics: pd.DataFrame, out_path: Path) -> None:
    # df_metrics index: model names; columns: metrics
    data = df_metrics.values.astype(float)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    im = ax.imshow(data, aspect="auto")
    ax.set_xticks(np.arange(df_metrics.shape[1]), labels=df_metrics.columns)
    ax.set_yticks(np.arange(df_metrics.shape[0]), labels=df_metrics.index)
    ax.set_title("Model vs Metrics (SMS Spam Classification)")
    # annotate cells
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved heatmap: {out_path}")

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    train_dir = root / "train"
    app_dir = root / "app"
    app_dir.mkdir(exist_ok=True)

    df = load_data(train_dir)
    df["text"] = df["text"].map(clean_text)
    df = df.dropna(subset=["text", "label"])

    X = df["text"].astype(str)
    y = df["label"].astype(str)

    X_train_txt, X_test_txt, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=None,
        ngram_range=(1, 2),
        min_df=2 if len(df) > 50 else 1,
        max_features=20000
    )
    X_train = vectorizer.fit_transform(X_train_txt)
    X_test = vectorizer.transform(X_test_txt)

    candidates = [
        ("MultinomialNB", MultinomialNB()),
        ("LogisticRegression", LogisticRegression(max_iter=2000)),
        ("LinearSVC", LinearSVC()),
    ]

    results = []
    for name, est in candidates:
        res = evaluate_model(name, est, X_train, X_test, y_train, y_test)
        results.append(res)
        print(f"{name}: acc={res['accuracy']:.4f} f1={res['f1']:.4f}")

    metrics_df = pd.DataFrame(results).drop(columns=["estimator"]).set_index("model")
    metrics_only = metrics_df[["accuracy", "precision", "recall", "f1"]]
    plot_heatmap(metrics_only, train_dir / "metrics_heatmap.png")

    # pick best by F1
    best = max(results, key=lambda r: r["f1"])
    print(f"Best model by F1: {best['model']} (f1={best['f1']:.4f})")

    joblib.dump(vectorizer, app_dir / "vectorizer.pkl")
    joblib.dump(best["estimator"], app_dir / "model.pkl")
    print("Saved artifacts to app/: vectorizer.pkl, model.pkl")

if __name__ == "__main__":
    main()
