#!/usr/bin/env python3
"""Validate data/ and write a data-quality report.

    python scripts/check.py            # exit 1 if there are errors
    python scripts/check.py --quiet    # only print the summary line

Errors (break the build): invalid structure, unknown category/type/tag, bad links,
duplicate ids. Warnings (listed in reports/data-quality.md): likely duplicates,
missing links/years/venues, venue that disagrees with the citation, entries
flagged for review, and so on.
"""
import argparse
import datetime
import os
import re
import sys
import unicodedata
from collections import defaultdict

from catalog import PREPRINT_VENUES, ROOT, load_entries, load_venues, load_vocab, utf8_stdout

LINK_KEYS = {"paper", "preprint", "code", "weights", "project", "dataset", "docs", "video"}
COMMON = {"id", "kind", "aliases", "title", "year", "venue", "venue_detail", "tags", "key", "links", "citation",
          "reviewed", "review_notes", "added", "sources", "review_basis", "_file"}
MODEL_FIELDS = COMMON | {"name", "category", "modality", "architecture", "task", "model_card", "inputs", "outputs",
                         "architecture_family", "code_status", "perturbation_type", "generalization"}
# field -> vocab list it must come from (list fields may hold several values)
VOCAB_FIELDS = {"inputs": "inputs", "outputs": "outputs", "architecture_family": "architecture_families",
                "code_status": "code_status", "review_basis": "review_basis",
                "perturbation_type": "perturbation_types", "generalization": "generalization",
                "interp_method": "interp_methods"}
RESOURCE_FIELDS = COMMON | {"type", "evaluates", "findings", "interp_method"}
URL = re.compile(r"^https?://[^\s<>\"]+$")
MAX_YEAR = datetime.date.today().year + 1

# Longest names first so "Nature Methods" wins over "Nature".
JOURNALS = sorted([
    "Nature Methods", "Nature Communications", "Nature Biotechnology", "Nature Machine Intelligence",
    "Nature Computational Science", "Nature Biomedical Engineering", "Nature Genetics",
    "Nature Cell Biology", "Nature Medicine", "Nature Reviews Genetics", "Genome Biology",
    "Genome Research", "Cell Systems", "Cell Genomics", "Cell Research", "Cell Reports Methods",
    "Cell Reports", "Briefings in Bioinformatics", "Bioinformatics", "Nucleic Acids Research",
    "Advanced Science", "National Science Review", "Patterns", "iScience", "PNAS", "Science", "Nature", "Cell",
], key=len, reverse=True)
ABSTRACT_START = re.compile(r"^(we |here,? we |present |propose |introduce |this (paper|study|work) )", re.I)


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", t)


def doi_of(url):
    m = re.search(r"(10\.\d{4,9}/[^\s?#]+)", url or "")
    if not m:
        return None
    d = m.group(1).lower().rstrip(".")
    d = re.sub(r"(\.full(\.pdf)?|\.abstract|\.pdf)$", "", d)
    if d.startswith(("10.1101/", "10.64898/")):  # bioRxiv/medRxiv: v1, v2... are the same paper
        d = re.sub(r"v\d+$", "", d)
    return d


def citation_journal(cit, title=""):
    """Journal named in a citation string, ignoring the quoted paper title."""
    low = re.sub(r'"[^"]*"|“[^”]*”', " ", cit or "").lower()
    low = low.replace("springer nature", " ")  # the publisher, not the journal Nature
    if title:
        low = low.replace(title.lower(), " ")
    for j in JOURNALS:
        if re.search(r"(?<![a-z])" + re.escape(j.lower()) + r"(?![a-z])", low):
            return j
    return None


class Report:
    def __init__(self):
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)

    def err(self, check, e, msg=""):
        self.errors[check].append((e.get("_file", "?"), msg))

    def warn(self, check, e, msg=""):
        self.warnings[check].append((e.get("_file", "?"), msg))


def check_entry(e, kind, vocab, rep):
    fname = os.path.splitext(os.path.basename(e["_file"]))[0]
    allowed = MODEL_FIELDS if kind == "model" else RESOURCE_FIELDS
    for k in e:
        if k not in allowed:
            rep.err("Unknown field", e, f"`{k}`")
    if e.get("id") != fname:
        rep.err("id must match file name", e, f"id `{e.get('id')}`")
    if e.get("kind") != kind:
        rep.err("Wrong kind", e, f"`{e.get('kind')}` in data/{kind}s/")
    if not e.get("title"):
        rep.err("Missing title", e)

    cats = {c["id"] for c in vocab["categories"]}
    types = {t["id"] for t in vocab["resource_types"]}
    tags = {t["id"] for t in vocab["tags"]}
    if kind == "model":
        if not e.get("name"):
            rep.err("Missing name", e)
        if e.get("category") not in cats:
            rep.err("Unknown category", e, f"`{e.get('category')}`")
        for k in (e.get("model_card") or {}):
            if k not in vocab["model_card_fields"]:
                rep.err("Unknown model_card field", e, f"`{k}`")
    else:
        if e.get("type") not in types:
            rep.err("Unknown resource type", e, f"`{e.get('type')}`")

    for t in e.get("tags") or []:
        if t not in tags:
            rep.err("Unknown tag", e, f"`{t}`")
    for field, vlist in VOCAB_FIELDS.items():
        allowed_v = {x["id"] for x in vocab.get(vlist) or []}
        for v in ([] if e.get(field) is None else e[field] if isinstance(e[field], list) else [e[field]]):
            if v not in allowed_v:
                rep.err(f"Unknown {field} value", e, f"`{v}`")
    if "added" in e and not (isinstance(e["added"], datetime.date) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e["added"]))):
        rep.err("Bad added date", e, f"`{e['added']}` (use YYYY-MM-DD)")
    for u in e.get("sources") or []:
        if not isinstance(u, str) or not URL.match(u):
            rep.err("Malformed source", e, f"`{u}`")
    y = e.get("year")
    if y is not None and not (isinstance(y, int) and 1990 <= y <= MAX_YEAR):
        rep.err("Bad year", e, f"`{y}`")
    for k, v in (e.get("links") or {}).items():
        if k not in LINK_KEYS:
            rep.err("Unknown link type", e, f"`{k}`")
        if not isinstance(v, str) or not URL.match(v):
            rep.err("Malformed link", e, f"{k}: `{v}`")
        elif v.count("(") != v.count(")"):
            rep.warn("Link may be truncated", e, v)

    # ---- warnings ----
    links = e.get("links") or {}
    # Databases and portals (a dataset/tool with its own site) have no single paper, venue or year.
    living = kind == "resource" and e.get("type") in ("dataset", "tool") and \
        any(links.get(k) for k in ("dataset", "project", "docs"))
    if not links.get("paper") and not links.get("preprint") and not living:
        rep.warn("No paper link", e)
    if kind == "model" and not links.get("code") and not e.get("code_status"):
        rep.warn("No code link", e)
    if y is None and not living:
        rep.warn("No year", e)
    venue = e.get("venue") or ""
    if not venue and not living:
        rep.warn("No venue", e)
    if not e.get("tags"):
        rep.warn("No tags", e)
    cj = citation_journal(e.get("citation"), e.get("title") or "")
    # A citation that names the entry's own venue agrees with it, even if a shorter journal name also matches
    # (e.g. "Science Advances" contains "Science").
    names_venue = venue and venue.lower() in (e.get("citation") or "").lower()
    if cj and venue and cj.lower() != venue.lower() and not names_venue:
        if venue.lower() in PREPRINT_VENUES:
            rep.warn("Preprint that may now be published", e, f"venue `{venue}`, citation mentions *{cj}*")
        elif venue.lower() not in {"neurips", "icml", "iclr", "aaai"}:
            rep.warn("Venue disagrees with citation", e, f"venue `{venue}`, citation mentions *{cj}*")
    title = e.get("title") or ""
    if venue == "Cell" and "cell" in title.lower() and not re.search(r"cell\.com|10\.1016/", " ".join(links.values())):
        rep.warn("Venue 'Cell' unconfirmed (title contains 'cell', no Cell link)", e)
    key = e.get("key") or ""
    if len(key) > 300:
        rep.warn("Key idea too long (over 300 characters)", e, f"{len(key)} characters")
    if ABSTRACT_START.match(key):
        rep.warn("Key idea looks copied from the abstract", e, key[:80] + "…")
    for n in e.get("review_notes") or []:
        rep.warn("Flagged for review", e, n)


def check_cross(models, resources, rep):
    all_e = models + resources
    ids = defaultdict(list)
    for e in all_e:
        ids[e.get("id")].append(e)
    for i, es in ids.items():
        if len(es) > 1:
            for e in es:
                rep.err("Duplicate id", e, f"`{i}`")

    by_title, by_doi, by_url = defaultdict(list), defaultdict(list), defaultdict(list)
    for e in all_e:
        if e.get("title"):
            by_title[norm(e["title"])].append(e)
        for u in (e.get("links") or {}).values():
            if not isinstance(u, str):
                continue
            d = doi_of(u)
            if d:
                by_doi[d].append(e)
            elif "github.com" not in u:
                by_url[u.rstrip("/")].append(e)
    for groups, label in ((by_title, "Same title"), (by_doi, "Same DOI"), (by_url, "Same paper URL")):
        for k, es in groups.items():
            uniq = {x["_file"]: x for x in es}
            if len(uniq) > 1:
                others = ", ".join(sorted(uniq))
                for e in uniq.values():
                    rep.warn(f"Possible duplicate ({label})", e, others)

    names = defaultdict(list)
    for m in models:
        for n in [m.get("name")] + (m.get("aliases") or []):
            if n:
                names[norm(n)].append(m)
    for k, es in names.items():
        uniq = {x["_file"]: x for x in es}
        if len(uniq) > 1:
            for e in uniq.values():
                rep.warn("Possible duplicate (Same model name)", e, ", ".join(sorted(uniq)))

    model_ids = {m["id"] for m in models}
    for r in resources:
        for mid in r.get("evaluates") or []:
            if mid not in model_ids:
                rep.err("`evaluates` points to an unknown model", r, f"`{mid}`")
        if "findings" in r and not isinstance(r["findings"], str):
            rep.err("`findings` must be one line of text", r, "")


def write_report(rep, models, resources):
    reviewed = sum(1 for e in models + resources if e.get("reviewed"))
    L = ["# Data quality report", "",
         f"Generated by `scripts/check.py` on {datetime.date.today().isoformat()}. Do not edit by hand.", "",
         f"- **{len(models)}** models, **{len(resources)}** resources; "
         f"**{reviewed}** marked `reviewed: true`.",
         f"- **{sum(map(len, rep.errors.values()))}** errors, "
         f"**{sum(map(len, rep.warnings.values()))}** warnings.", "", "## Summary", "",
         "| Check | Level | Entries |", "|---|---|---|"]
    for level, d in (("error", rep.errors), ("warning", rep.warnings)):
        for check in sorted(d, key=lambda c: -len(d[c])):
            L.append(f"| {check} | {level} | {len(d[check])} |")
    for level, d in (("Errors", rep.errors), ("Warnings", rep.warnings)):
        if not d:
            continue
        L += ["", f"## {level}"]
        for check in sorted(d, key=lambda c: -len(d[c])):
            L += ["", f"### {check} ({len(d[check])})", ""]
            for f, msg in sorted(d[check]):
                L.append(f"- [`{os.path.basename(f)}`](../{f})" + (f" — {msg}" if msg else ""))
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "data-quality.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    vocab = load_vocab()
    models, resources = load_entries("models"), load_entries("resources")
    load_venues()
    rep = Report()
    for e in models:
        check_entry(e, "model", vocab, rep)
    for e in resources:
        check_entry(e, "resource", vocab, rep)
    check_cross(models, resources, rep)
    write_report(rep, models, resources)

    n_err = sum(map(len, rep.errors.values()))
    n_warn = sum(map(len, rep.warnings.values()))
    if not args.quiet:
        for check, items in rep.errors.items():
            for f, msg in items:
                print(f"ERROR  {check}: {f} {msg}")
    print(f"{n_err} errors, {n_warn} warnings → reports/data-quality.md")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
