#!/usr/bin/env python3
"""Create a new model or resource YAML file, refusing obvious duplicates.

Model:
    python scripts/new_entry.py model --name scGPT \
        --title "scGPT: toward building a foundation model ..." --year 2024 \
        --venue "Nature Methods" --category multimodal --tags multi-omics,generative \
        --paper https://doi.org/10.1038/s41592-024-02201-0 --code https://github.com/bowang-lab/scGPT

Resource:
    python scripts/new_entry.py resource --type benchmark \
        --title "Zero-shot evaluation reveals limitations of single-cell foundation models" \
        --year 2025 --venue "Genome Biology" --paper https://... --evaluates scgpt,geneformer

Categories, resource types and tags must exist in data/vocab.yaml.
The file is written with `reviewed: false`; then run check.py and build.py.
"""
import argparse
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import DATA, load_entries, load_vocab, slug, write_yaml  # noqa: E402
from check import doi_of, norm  # noqa: E402


def csv_list(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["model", "resource"])
    ap.add_argument("--title", required=True)
    ap.add_argument("--name", help="model name (models only)")
    ap.add_argument("--category", help="category id from data/vocab.yaml (models only)")
    ap.add_argument("--type", help="resource type id from data/vocab.yaml (resources only)")
    ap.add_argument("--year", type=int)
    ap.add_argument("--venue", default="")
    ap.add_argument("--tags", default="", help="comma-separated tag ids")
    ap.add_argument("--modality", default="")
    ap.add_argument("--architecture", default="")
    ap.add_argument("--key", default="", help="one line, in your own words")
    ap.add_argument("--paper", default="")
    ap.add_argument("--code", default="")
    ap.add_argument("--weights", default="")
    ap.add_argument("--project", default="")
    ap.add_argument("--evaluates", default="", help="comma-separated model ids (resources only)")
    ap.add_argument("--citation", default="")
    a = ap.parse_args()

    vocab = load_vocab()
    if a.kind == "model":
        if not a.name or not a.category:
            sys.exit("error: models need --name and --category")
        if a.category not in {c["id"] for c in vocab["categories"]}:
            sys.exit(f"error: unknown category '{a.category}'. Options: "
                     + ", ".join(c["id"] for c in vocab["categories"]))
    elif a.type not in {t["id"] for t in vocab["resource_types"]}:
        sys.exit("error: resources need --type, one of: " + ", ".join(t["id"] for t in vocab["resource_types"]))
    tags = csv_list(a.tags)
    bad = [t for t in tags if t not in {t["id"] for t in vocab["tags"]}]
    if bad:
        sys.exit(f"error: unknown tag(s) {bad}. Add them to data/vocab.yaml first.")

    existing = load_entries("models") + load_entries("resources")
    t, d = norm(a.title), doi_of(a.paper)
    for e in existing:
        same_doi = d and any(doi_of(u) == d for u in (e.get("links") or {}).values())
        same_name = a.name and norm(a.name) in {norm(n) for n in [e.get("name")] + (e.get("aliases") or []) if n}
        if norm(e.get("title")) == t or same_doi or same_name:
            sys.exit(f"error: looks like a duplicate of {e['_file']}. Edit that file instead.")

    used = {e["id"] for e in existing}
    base = slug(a.name, 4) if a.kind == "model" else slug(a.title, 6)
    eid, i = base, 2
    while eid in used:
        eid, i = f"{base}-{i}", i + 1

    links = OrderedDict((k, getattr(a, k)) for k in ("paper", "code", "weights", "project") if getattr(a, k))
    e = OrderedDict(id=eid, kind=a.kind)
    if a.kind == "model":
        e.update(name=a.name, title=a.title, year=a.year, venue=a.venue, category=a.category, tags=tags,
                 modality=a.modality, architecture=a.architecture, key=a.key, links=links)
    else:
        e.update(type=a.type, title=a.title, year=a.year, venue=a.venue, tags=tags, key=a.key,
                 links=links, evaluates=csv_list(a.evaluates))
    e.update(citation=a.citation, reviewed=False)
    e = OrderedDict((k, v) for k, v in e.items() if v not in ("", None, [], {}) or k == "reviewed")

    path = os.path.join(DATA, f"{a.kind}s", f"{eid}.yaml")
    write_yaml(path, e)
    print(f"wrote {os.path.relpath(path)} — now run: python scripts/check.py && python scripts/build.py")


if __name__ == "__main__":
    main()
