#!/usr/bin/env python3
"""
Generate README.md from data/*.csv.

The CSV files in data/ are the SINGLE SOURCE OF TRUTH.
Never hand-edit the model/resource/venue tables in README.md directly --
edit the CSVs and re-run this script:

    python scripts/generate_readme.py

This keeps the list diff-friendly, sortable, and easy to extend.
"""
import csv, os, datetime
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# Order in which model categories appear in the README.
CATEGORY_ORDER = [
    "scRNA-seq / Transcriptomics Foundation Models",
    "Spatial & Spatial Multi-omics",
    "Epigenomics & Chromatin Accessibility (scATAC)",
    "Multimodal & Multi-omics Integration",
    "Proteomics & Protein-level Models",
    "Sequence-to-Expression & Regulatory Genomics",
    "Gene Regulatory Networks & Graph-based Models",
    "Generative Models (Diffusion / Flow / VAE)",
    "Cell Morphology & Imaging Models",
    "LLM-based & Language-Cell Models",
    "Agentic & Autonomous Cell Models",
    "Cross-species & Cell Atlas / Similarity Models",
    "Perturbation Prediction & Virtual Cell / World Models",
    "Other Single-cell Foundation Models",
]

def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def anchor(text):
    out = "".join(c for c in text.lower() if c.isalnum() or c in " -").strip()
    return out.replace(" ", "-")

def trunc(s, n=160):
    s = (s or "").replace("\n", " ").replace("|", "\\|").strip()
    return (s[: n - 1].rstrip() + "…") if len(s) > n else s

def links_cell(paper, code):
    parts = []
    if paper: parts.append(f"[paper]({paper})")
    if code:  parts.append(f"[code]({code})")
    return " · ".join(parts) if parts else "—"

def year_key(r):
    try: return int(r.get("year") or 0)
    except ValueError: return 0

def main():
    models = load("models.csv")
    resources = load("resources.csv")
    venues = load("venues.csv")

    by_cat = defaultdict(list)
    for m in models:
        by_cat[m.get("category") or "Other Single-cell Foundation Models"].append(m)

    cats = [c for c in CATEGORY_ORDER if c in by_cat]
    cats += [c for c in by_cat if c not in CATEGORY_ORDER]

    L = []
    L.append("# Awesome Single-Cell Foundation Models & Virtual Cell Modelling [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)")
    L.append("")
    L.append("> A curated, categorised list of foundation models for single-cell biology and AI virtual-cell / world models, "
             "plus the benchmarks, perspectives, surveys and venues that surround them.")
    L.append("")
    L.append(f"**{len(models)} models · {len(resources)} benchmarks/surveys/perspectives · {len(venues)} venues** · "
             f"last generated {datetime.date.today().isoformat()}.")
    L.append("")
    L.append("This list is generated from machine-readable CSVs. **Do not edit the tables below by hand** — "
             "edit [`data/models.csv`](data/models.csv), [`data/resources.csv`](data/resources.csv) or "
             "[`data/venues.csv`](data/venues.csv) and run `python scripts/generate_readme.py`. "
             "See [CONTRIBUTING.md](CONTRIBUTING.md).")
    L.append("")

    # ---- Contents ----
    L.append("## Contents")
    L.append("")
    L.append("**Models**")
    for c in cats:
        L.append(f"- [{c}](#{anchor(c)}) ({len(by_cat[c])})")
    L.append("")
    L.append("**Resources**")
    L.append("- [Benchmarks & Evaluation](#benchmarks--evaluation)")
    L.append("- [Datasets & Atlases](#datasets--atlases)")
    L.append("- [Tools & Software](#tools--software)")
    L.append("- [Perspectives & Surveys](#perspectives--surveys)")
    L.append("- [Other Resources](#other-resources)")
    L.append("- [Where to Publish & Track New Work](#where-to-publish--track-new-work)")
    L.append("")

    # ---- Models ----
    L.append("## Models")
    L.append("")
    for c in cats:
        rows = sorted(by_cat[c], key=year_key, reverse=True)
        L.append(f"### {c}")
        L.append("")
        L.append("| Model | Year | Venue | Modality | Architecture | Key idea | Links |")
        L.append("|---|---|---|---|---|---|---|")
        for r in rows:
            L.append("| {model} | {year} | {venue} | {mod} | {arch} | {key} | {links} |".format(
                model=f"**{trunc(r.get('model'),40)}**",
                year=r.get("year") or "",
                venue=trunc(r.get("venue"), 22) or "—",
                mod=trunc(r.get("modality"), 32) or "—",
                arch=trunc(r.get("arch"), 32) or "—",
                key=trunc(r.get("key") or r.get("task"), 150) or "—",
                links=links_cell(r.get("paper"), r.get("code")),
            ))
        L.append("")

    # ---- Resources ----
    def res_section(title, types):
        rs = sorted([r for r in resources if r.get("type") in types], key=year_key, reverse=True)
        if not rs: return
        L.append(f"## {title}")
        L.append("")
        L.append("| Title | Year | Venue | Notes | Links |")
        L.append("|---|---|---|---|---|")
        for r in rs:
            link = r.get("paper") or r.get("links")
            L.append("| {t} | {y} | {v} | {n} | {l} |".format(
                t=trunc(r.get("title"), 90), y=r.get("year") or "",
                v=trunc(r.get("venue"), 20) or "—", n=trunc(r.get("key"), 150) or "—",
                l=f"[link]({link})" if link else "—"))
        L.append("")

    res_section("Benchmarks & Evaluation", {"Evaluation"})
    res_section("Datasets & Atlases", {"Dataset"})
    res_section("Tools & Software", {"Tool"})
    res_section("Perspectives & Surveys",
                {"Perspective", "Survey", "Nature Biotech Editorial Paper", "Research statement"})
    res_section("Other Resources", {"Reference"})

    # ---- Venues ----
    if venues:
        L.append("## Where to Publish & Track New Work")
        L.append("")
        L.append("| Venue | Type | Notes | Link |")
        L.append("|---|---|---|---|")
        for v in venues:
            L.append("| {n} | {t} | {d} | {l} |".format(
                n=trunc(v.get("name"), 50), t=trunc(v.get("type"), 16) or "—",
                d=trunc(v.get("desc"), 160) or "—",
                l=f"[link]({v.get('link')})" if v.get("link") else "—"))
        L.append("")

    L.append("## Contributing")
    L.append("")
    L.append("Add a row to the relevant CSV in [`data/`](data/) and run "
             "`python scripts/generate_readme.py`, then open a PR. Full instructions in "
             "[CONTRIBUTING.md](CONTRIBUTING.md).")
    L.append("")
    L.append("## License")
    L.append("")
    L.append("[CC0-1.0](LICENSE) — to the extent possible under law, contributors have waived all "
             "copyright to this curation. Linked papers remain under their own licenses.")
    L.append("")

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print(f"Wrote README.md: {len(models)} models across {len(cats)} categories, "
          f"{len(resources)} resources, {len(venues)} venues.")

if __name__ == "__main__":
    main()
