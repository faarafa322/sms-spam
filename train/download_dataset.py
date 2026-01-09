
"""
Download and prepare the SMS Spam Collection dataset from UCI.
Source: https://archive.ics.uci.edu/dataset/228/sms+spam+collection

It downloads the ZIP, extracts SMSSpamCollection, and saves a clean CSV:
  train/sms_spam.csv   columns: label,text
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/228/sms%2Bspam%2Bcollection.zip"

def main() -> None:
    root = Path(__file__).resolve().parent
    out_csv = root / "sms_spam.csv"

    print(f"Downloading: {UCI_ZIP_URL}")
    r = requests.get(UCI_ZIP_URL, timeout=60)
    r.raise_for_status()

    z = zipfile.ZipFile(io.BytesIO(r.content))
    # file is usually named 'SMSSpamCollection' inside the zip
    target_name = None
    for name in z.namelist():
        if name.lower().endswith("smsspamcollection"):
            target_name = name
            break
    if target_name is None:
        raise RuntimeError(f"SMSSpamCollection not found in zip. Found: {z.namelist()}")

    raw = z.read(target_name).decode("utf-8", errors="replace").splitlines()
    rows = []
    for line in raw:
        # each line: label \t message
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        label, text = parts[0].strip(), parts[1].strip()
        if label not in {"ham", "spam"} or not text:
            continue
        rows.append((label, text))

    df = pd.DataFrame(rows, columns=["label", "text"])
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df):,} rows to {out_csv}")

if __name__ == "__main__":
    main()
