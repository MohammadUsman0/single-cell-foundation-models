#!/usr/bin/env python3
"""One-off migration: data/*.csv -> data/models/*.yaml, data/resources/*.yaml, data/venues.yaml.

Kept in the repo so the migration can be re-run or audited. It is faithful to the
CSVs: it never invents metadata. The only changes it makes are listed in
MIGRATION_LOG (written to reports/migration-log.md):

  * venue spelling normalised (e.g. "Nature Comp. Science" -> "Nature Computational Science")
  * values that are not venues (e.g. "© by Noetik") moved out of `venue` into a review note
  * duplicate rows with the same normalised title merged
  * placeholder values ("-", "—", "unknown") dropped
  * an obviously truncated URL removed (kept in a review note)
  * resource types outside the old schema mapped to the closest type and flagged
  * tags derived from category, modality text and title keywords (marked for review)

The source CSVs were removed after migration; to re-run, restore them first:
    git show daaa7e1:data/models.csv > data/models.csv   (same for resources.csv, venues.csv)

Usage:  python scripts/legacy/migrate_csv.py
"""
import csv, os, re, sys, unicodedata
from collections import OrderedDict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
LOG = []

CATEGORY_IDS = {
    "scRNA-seq / Transcriptomics Foundation Models": "scrna",
    "Spatial & Spatial Multi-omics": "spatial",
    "Epigenomics & Chromatin Accessibility (scATAC)": "epigenomics",
    "Multimodal & Multi-omics Integration": "multimodal",
    "Proteomics & Protein-level Models": "proteomics",
    "Sequence-to-Expression & Regulatory Genomics": "seq2exp",
    "Gene Regulatory Networks & Graph-based Models": "grn",
    "Generative Models (Diffusion / Flow / VAE)": "generative",
    "Cell Morphology & Imaging Models": "morphology",
    "LLM-based & Language-Cell Models": "llm",
    "Agentic & Autonomous Cell Models": "agents",
    "Cross-species & Cell Atlas / Similarity Models": "atlas",
    "Perturbation Prediction & Virtual Cell / World Models": "perturbation",
    "Other Single-cell Foundation Models": "other",
}

RESOURCE_TYPES = {
    "Evaluation": "benchmark", "Dataset": "dataset", "Tool": "tool",
    "Survey": "survey", "Perspective": "perspective", "Reference": "reference",
}

# venue -> (canonical venue, detail)
VENUE_FIX = {
    "Nature Biomedical Eng.": ("Nature Biomedical Engineering", None),
    "Nature Comp. Science": ("Nature Computational Science", None),
    "Iscience": ("iScience", None),
    "ICLR Poster": ("ICLR", "poster"),
    "ICML Poster": ("ICML", "poster"),
    "NeurIPS Poster": ("NeurIPS", "poster"),
    "NeurIPS Datasets and Benchmarks Track": ("NeurIPS", "Datasets and Benchmarks Track"),
    "ICML Workshop GenBio": ("ICML", "GenBio Workshop"),
    "Nature Biotechnology Comment": ("Nature Biotechnology", "Comment"),
}
NOT_A_VENUE = re.compile(r"^©")

# Known non-model rows (from CLAUDE.md starter tasks + review of the data).
LIKELY_NOT_MODEL = {
    "Spatial Perturb-seq": "an assay / dataset, not a model",
    "CRISPRi Map": "a perturbation dataset, not a model",
    "Perturb-FISH": "an assay / dataset, not a model",
    "Comment": "a Nature Biotechnology comment, not a model; the name field is a placeholder",
    "Theory": "name field looks like a placeholder; check whether this is a model",
    "Stanford PhD Thesis": "a PhD thesis, not a model; the name field is a placeholder",
    "Cell Maps": "may be a dataset / resource rather than a model",
}

PLACEHOLDER = {"", "-", "—", "–", "unknown", "n/a", "na"}

TAG_RULES = [  # (tag, regex over modality+title+architecture)
    ("scatac-seq", r"\batac|chromatin access"),
    ("spatial", r"spatial|niche|tissue architecture"),
    ("proteomics", r"proteom|protein\b|cite-seq"),
    ("histology", r"histolog|histopath|\bh&e\b|whole[- ]slide|\bwsi\b|patholog"),
    ("imaging", r"cell painting|morpholog|microscop|imag"),
    ("multi-omics", r"multi-?omic|multi-?modal"),
    ("text", r"\btext\b|language model|\bllm|chatgpt|gpt-4|natural language"),
    ("dna-sequence", r"dna sequence|from sequence|sequence-to|genom(e|ic) language"),
    ("perturbation", r"perturb|crispr|knock-?out|drug response|intervention"),
    ("drug-response", r"\bdrug|compound|chemical perturb"),
    ("gene-regulation", r"gene regulat|regulatory network|\bgrn\b|regulatory"),
    ("cross-species", r"cross-species|across species|species-agnostic|evolution"),
    ("virtual-cell", r"virtual cell|virtual-cell|world model|digital (organism|cell)"),
    ("generative", r"diffusion|flow matching|\bvae\b|variational|generative"),
    ("graph", r"\bgraph|\bgnn\b"),
    ("agent", r"\bagent|agentic|autonomous"),
    ("scrna-seq", r"scrna|single-cell rna|single cell rna|transcriptom|gene expression"),
]
CATEGORY_TAGS = {
    "scrna": ["scrna-seq"], "spatial": ["spatial"],
    "epigenomics": ["scatac-seq"], "multimodal": ["multi-omics"],
    "proteomics": ["proteomics"], "seq2exp": ["dna-sequence"],
    "grn": ["gene-regulation"], "generative": ["generative"],
    "morphology": ["imaging"], "llm": ["llm"], "agents": ["agent"],
    "atlas": [], "perturbation": ["perturbation"], "other": [],
}


def clean(v):
    v = (v or "").strip()
    return "" if v.lower() in PLACEHOLDER else v


def slug(text, max_words=6):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", " ", t).strip().lower().split()
    return "-".join(t[:max_words]) or "entry"


def norm_title(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", t)


def derive_tags(cat, text):
    tags = list(CATEGORY_TAGS.get(cat, []))
    low = text.lower()
    for tag, rx in TAG_RULES:
        if re.search(rx, low) and tag not in tags:
            tags.append(tag)
    return tags


def fix_venue(venue, notes, label):
    if not venue:
        return "", None
    if NOT_A_VENUE.search(venue):
        notes.append(f"venue field said '{venue}', which is not a venue; left blank")
        LOG.append(f"- {label}: venue '{venue}' is not a venue → blank")
        return "", None
    if venue in VENUE_FIX:
        new, detail = VENUE_FIX[venue]
        LOG.append(f"- {label}: venue '{venue}' → '{new}'" + (f" (detail: {detail})" if detail else ""))
        return new, detail
    return venue, None


def check_url(url, notes, label, field):
    if not url:
        return ""
    if url.count("(") != url.count(")"):
        notes.append(f"{field} link looked truncated and was removed: {url}")
        LOG.append(f"- {label}: truncated {field} link removed ({url})")
        return ""
    return url


def code_or_project(url):
    host = re.sub(r"^https?://([^/]+).*", r"\1", url).lower()
    if any(h in host for h in ("github.com", "gitlab", "bitbucket", "huggingface.co", "zenodo", "doi.org")):
        return "code"
    return "project"


def to_year(v):
    v = clean(v)
    return int(v) if v.isdigit() else None


def drop_empty(d):
    out = OrderedDict()
    for k, v in d.items():
        if isinstance(v, dict):
            v = drop_empty(v)
        if v in ("", None, [], {}):
            continue
        out[k] = v
    return out


def migrate_models(rows):
    entries = []
    for r in rows:
        name = clean(r["model"])
        notes = []
        cat = CATEGORY_IDS.get(r["category"].strip())
        if not cat:
            notes.append(f"unknown category '{r['category']}' → other")
            cat = "other"
        venue, detail = fix_venue(clean(r["venue"]), notes, name)
        paper = check_url(clean(r["paper"]), notes, name, "paper")
        code_raw = check_url(clean(r["code"]), notes, name, "code")
        links = OrderedDict(paper=paper)
        if code_raw:
            kind = code_or_project(code_raw)
            links[kind] = code_raw
            if kind == "project":
                notes.append(f"code field pointed to a non-code site ({code_raw}); stored as project link")
                LOG.append(f"- {name}: code link {code_raw} stored as project")
        if name in LIKELY_NOT_MODEL:
            notes.append("possibly not a model: " + LIKELY_NOT_MODEL[name])
        key, task = clean(r["key"]), clean(r["task"])
        if task and task == key:
            task = ""
        text = " ".join([r["modality"], r["title"], r["arch"], name])
        e = OrderedDict(
            id=None, kind="model", name=name, title=clean(r["title"]), year=to_year(r["year"]),
            venue=venue, venue_detail=detail, category=cat, tags=derive_tags(cat, text),
            modality=clean(r["modality"]), architecture=clean(r["arch"]), task=task, key=key,
            links=links, citation=clean(r["citation"]), reviewed=False, review_notes=notes,
        )
        entries.append(e)
    return entries


def migrate_resources(rows):
    entries = []
    for r in rows:
        title = clean(r["title"])
        notes = []
        t = r["type"].strip()
        rtype = RESOURCE_TYPES.get(t)
        if not rtype:
            rtype = "perspective"
            notes.append(f"type was '{t}' (not in the old schema); mapped to perspective")
            LOG.append(f"- resource '{title[:50]}': type '{t}' → perspective")
        venue, detail = fix_venue(clean(r["venue"]), notes, title[:50])
        # A title that contains a full citation, e.g. "X. Nat Biotechnol (2026). https://doi..."
        m = re.match(r"^(.*?)\.\s+(Nat Biotechnol)\s+\((\d{4})\)\.\s+https?://\S+$", title)
        if m:
            LOG.append(f"- resource '{title[:50]}': title held a citation; title → '{m.group(1)}', venue → Nature Biotechnology")
            title, venue = m.group(1), venue or "Nature Biotechnology"
        paper = check_url(clean(r["paper"]), notes, title[:50], "paper")
        other = check_url(clean(r["links"]), notes, title[:50], "links")
        links = OrderedDict(paper=paper)
        if other:
            links[code_or_project(other)] = other
        text = " ".join([title, r["key"]])
        e = OrderedDict(
            id=None, kind="resource", type=rtype, title=title, year=to_year(r["year"]),
            venue=venue, venue_detail=detail, tags=derive_tags(None, text), key=clean(r["key"]),
            links=links, evaluates=[], citation=clean(r["citation"]), reviewed=False, review_notes=notes,
        )
        entries.append(e)
    return entries


def merge_duplicates(entries, label_field):
    seen, out = {}, []
    for e in entries:
        k = norm_title(e["title"])
        if k and k in seen:
            base = seen[k]
            for f, v in e.items():
                if f in ("id", "review_notes"):
                    continue
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        if vv and not base[f].get(kk):
                            base[f][kk] = vv
                elif isinstance(v, list):
                    base[f] = base[f] + [x for x in v if x not in base[f]]
                elif v and not base.get(f):
                    base[f] = v
            alt = e.get(label_field)
            if alt and alt != base.get(label_field):
                base.setdefault("aliases", [])
                base["aliases"].append(alt)
            base["review_notes"].append(f"merged duplicate row '{alt}' with the same title")
            LOG.append(f"- merged duplicate '{alt}' into '{base.get(label_field)}' (same title)")
            continue
        seen[k] = e
        out.append(e)
    return out


def assign_ids(entries, field, used):
    for e in entries:
        base = slug(e[field] if e.get(field) else e["title"], 4 if field == "name" else 6)
        i, sid = 2, base
        while sid in used:
            sid, i = f"{base}-{i}", i + 1
        used.add(sid)
        e["id"] = sid


def write_yaml(path, data):
    class Dumper(yaml.SafeDumper):
        pass
    Dumper.add_representer(OrderedDict, lambda d, v: d.represent_dict(v.items()))
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100)


def main():
    load = lambda n: list(csv.DictReader(open(os.path.join(DATA, n), encoding="utf-8")))
    models = merge_duplicates(migrate_models(load("models.csv")), "name")
    resources = merge_duplicates(migrate_resources(load("resources.csv")), "title")
    used = set()
    assign_ids(models, "name", used)
    assign_ids(resources, "title", used)

    for sub, entries in (("models", models), ("resources", resources)):
        d = os.path.join(DATA, sub)
        os.makedirs(d, exist_ok=True)
        for e in entries:
            e = drop_empty(e)
            if "aliases" in e:  # keep aliases next to the name
                order = list(e.keys())
                order.remove("aliases")
                order.insert(order.index("name" if "name" in e else "title") + 1, "aliases")
                e = OrderedDict((k, e[k]) for k in order)
            e.setdefault("reviewed", False)
            write_yaml(os.path.join(d, f"{e['id']}.yaml"), e)

    venues = [drop_empty(OrderedDict(name=clean(v["name"]), type=clean(v["type"]),
                                     desc=clean(v["desc"]), link=clean(v["link"])))
              for v in load("venues.csv")]
    write_yaml(os.path.join(DATA, "venues.yaml"), venues)

    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "migration-log.md"), "w", encoding="utf-8") as f:
        f.write("# CSV → YAML migration log\n\n")
        f.write(f"{len(models)} models, {len(resources)} resources, {len(venues)} venues written.\n\n")
        f.write("Every entry was migrated with `reviewed: false` and auto-derived tags; "
                "verification happens in phase 2.\n\nChanges made during migration:\n\n")
        f.write("\n".join(LOG) + "\n")
    print(f"{len(models)} models, {len(resources)} resources, {len(venues)} venues; {len(LOG)} logged changes")


if __name__ == "__main__":
    sys.exit(main())
