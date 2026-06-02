#!/usr/bin/env python3
"""
Add a model to data/models.csv and regenerate README.md.

Example:
    python scripts/add_paper.py \
        --model "scGPT-2" \
        --title "scGPT-2: ..." \
        --year 2026 --venue bioRxiv \
        --category "scRNA-seq / Transcriptomics Foundation Models" \
        --modality "scRNA-seq" --arch "Transformer" \
        --key "One-line summary of the contribution." \
        --paper "https://..." --code "https://github.com/..."

Run with no required field missing; category should match one of the
headings in scripts/generate_readme.py (CATEGORY_ORDER). Unknown
categories are allowed but will render under their own heading.
"""
import csv, os, argparse, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "data", "models.csv")
COLS = ["model", "title", "year", "venue", "category", "modality",
        "arch", "task", "key", "paper", "code", "citation"]

def main():
    ap = argparse.ArgumentParser()
    for c in COLS:
        ap.add_argument(f"--{c}", default="")
    args = ap.parse_args()
    row = {c: getattr(args, c) for c in COLS}
    if not row["model"] or not row["title"]:
        sys.exit("error: --model and --title are required")

    existing = []
    if os.path.exists(CSV):
        with open(CSV, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    if any(r["model"].strip().lower() == row["model"].strip().lower() for r in existing):
        print(f"note: '{row['model']}' already present — skipping duplicate.")
        return
    existing.append(row)
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in existing:
            w.writerow({c: r.get(c, "") for c in COLS})
    print(f"added '{row['model']}' ({len(existing)} models total)")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "generate_readme.py")])

if __name__ == "__main__":
    main()
