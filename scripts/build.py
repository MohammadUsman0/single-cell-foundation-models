#!/usr/bin/env python3
"""Build every generated file from data/.

    python scripts/build.py

Writes:
  README.md               simple tagged list (never edit by hand)
  docs/data.json          full catalogue for the GitHub Pages site
  exports/models.csv      flat CSV of models
  exports/resources.csv   flat CSV of resources
  exports/catalogue.bib   BibTeX of every entry (for LaTeX, Zotero, Mendeley)
  exports/catalogue.ris   RIS of every entry (for Zotero, Mendeley, EndNote)
"""
import csv
import datetime
import json
import os
import re
from collections import defaultdict

from catalog import ROOT, github_repo, load_entries, load_venues, load_vocab, status, year_sort_key

REPO = "MohammadUsman0/single-cell-foundation-models"

RELATED_LISTS = [
    ("OmicsML/awesome-foundation-model-single-cell-papers",
     "Paper list organised around a review of single-cell foundation models."),
    ("Boom5426/Awesome-Virtual-Cell",
     "Virtual-cell papers, datasets and benchmarks with a searchable catalogue."),
    ("theislab/single-cell-transformer-papers",
     "Companion list to the Nature Methods review on transformers in single-cell omics."),
    ("KatarinaYuan/awesome-single-cell-foundation", "Paper and code collection by data type."),
    ("OmicsML/awesome-deep-learning-single-cell-papers", "Deep learning for single-cell analysis, by task."),
    ("seandavi/awesome-single-cell", "General single-cell software list."),
]


def site_url():
    """GitHub Pages address of the catalogue site (served from docs/ on main)."""
    owner, name = REPO.split("/")
    return f"https://{owner.lower()}.github.io/{name}/"


def anchor(text):
    out = "".join(c for c in text.lower() if c.isalnum() or c in " -").strip()
    return out.replace(" ", "-")


def md_escape(s):
    return (s or "").replace("\n", " ").replace("[", "\\[").replace("]", "\\]").strip()


def entry_line(e, tag_labels):
    parts = []
    if e.get("name"):
        parts.append(f"**{md_escape(e['name'])}**")
    title = md_escape(e.get("title"))
    venue_year = " ".join(str(x) for x in (e.get("venue"), e.get("year")) if x)
    if venue_year:
        detail = f", {e['venue_detail']}" if e.get("venue_detail") else ""
        parts.append(f"{title} (**{venue_year}**{detail})")
    else:
        parts.append(title)
    tags = [tag_labels[t] for t in e.get("tags", []) if t in tag_labels]
    if tags:
        parts.append(" ".join(f"`{t}`" for t in tags))
    links = e.get("links") or {}
    link_md = [f"[[{k}]({links[k]})]" for k in ("paper", "code", "weights", "dataset", "project") if links.get(k)]
    repo = github_repo(links.get("code"))
    if repo:
        link_md.append(f"![stars](https://img.shields.io/github/stars/{repo}?style=flat-square&label=%E2%98%85)")
    if link_md:
        parts.append(" ".join(link_md))
    return "- " + " · ".join(parts)


def latest_additions(models, resources, dates=5):
    """README lines: how many entries were added on each recent date (from each entry's `added` field)."""
    by_date = defaultdict(list)
    for e in models + resources:
        if e.get("added"):
            by_date[str(e["added"])].append(e)
    if not by_date:
        return []
    L = ["## Latest Additions", "", "| Added | Models | Resources |", "|---|---|---|"]
    for d in sorted(by_date, reverse=True)[:dates]:
        es = by_date[d]
        L.append(f"| {d} | {sum(e['kind'] == 'model' for e in es)} | {sum(e['kind'] == 'resource' for e in es)} |")
    return L + ["", "Every entry records the date it was added (`added`), also in [`exports/`](exports/).", ""]


def build_readme(models, resources, venues, vocab):
    tag_labels = {t["id"]: t["label"] for t in vocab["tags"]}
    by_cat = defaultdict(list)
    for m in models:
        by_cat[m["category"]].append(m)
    cats = [c for c in vocab["categories"] if by_cat.get(c["id"])]
    by_type = defaultdict(list)
    for r in resources:
        by_type[r["type"]].append(r)
    types = [t for t in vocab["resource_types"] if by_type.get(t["id"])]
    n_code = sum(1 for m in models if (m.get("links") or {}).get("code"))

    L = [
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.png">',
        '  <img alt="Single-Cell Foundation Models &amp; Virtual Cell Modelling: models, benchmarks, datasets and '
        'tools for AI-driven single-cell biology" src="docs/assets/banner-light.png" width="100%">',
        "</picture>",
        "",
        "# Awesome Single-Cell Foundation Models & Virtual Cell Modelling "
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        f"[![Catalogue](https://img.shields.io/badge/catalogue-browse-0B6E99?style=flat-square)]({site_url()}) "
        f"[![Last commit](https://img.shields.io/github/last-commit/{REPO}?style=flat-square&label=updated)]"
        f"(https://github.com/{REPO}/commits/main) "
        f"[![Stars](https://img.shields.io/github/stars/{REPO}?style=flat-square)](https://github.com/{REPO}/stargazers) "
        "[![License: CC0-1.0](https://img.shields.io/badge/license-CC0--1.0-lightgrey?style=flat-square)](LICENSE)",
        "",
        "> A curated list of foundation models for single-cell biology and AI virtual-cell / world models, "
        "plus the benchmarks, datasets, tools and reviews around them.",
        "",
        f"**[Browse the catalogue →]({site_url()})** search, filter and compare models; "
        "every model has its own page.",
        "",
        "For each model, the catalogue aims to record what it is, whether you can use it "
        "(code, weights, license) and what benchmarks found about it. Titles, years, venues and links "
        "are verified against Crossref, OpenAlex, arXiv and bioRxiv with "
        "[`scripts/verify.py`](scripts/verify.py).",
        "",
        f"**{len(models)} models** ({n_code} with code) · **{len(resources)} resources** · "
        f"**{len(venues)} venues** · updated {datetime.date.today().isoformat()}",
        "",
        "Each entry: **name** · title (**venue year**) · tags · links. "
        "Machine-readable data: [`docs/data.json`](docs/data.json) · [`exports/`](exports/).",
        "",
        "> [!NOTE]",
        "> This README is generated from [`data/`](data/). Don't edit it by hand — see "
        "[CONTRIBUTING.md](CONTRIBUTING.md).",
        "",
        *latest_additions(models, resources),
        "## Contents",
        "",
        "**Models**",
        "",
    ]
    L += [f"- [{c['label']}](#{anchor(c['label'])}) ({len(by_cat[c['id']])})" for c in cats]
    L += ["", "**Resources**", ""]
    L += [f"- [{t['label']}](#{anchor(t['label'])}) ({len(by_type[t['id']])})" for t in types]
    L += ["- [Where to Publish & Track New Work](#where-to-publish--track-new-work)",
          "- [Related Lists](#related-lists)", "", "## Models", ""]

    for c in cats:
        L += [f"### {c['label']}", "", f"*{c['desc']}*", ""]
        L += [entry_line(m, tag_labels) for m in sorted(by_cat[c["id"]], key=year_sort_key)]
        L.append("")

    for t in types:
        L += [f"## {t['label']}", ""]
        L += [entry_line(r, tag_labels) for r in sorted(by_type[t["id"]], key=year_sort_key)]
        L.append("")

    if venues:
        L += ["## Where to Publish & Track New Work", ""]
        for v in venues:
            name = f"[{v['name']}]({v['link']})" if v.get("link") else v["name"]
            kind = f" *({v['type']})*" if v.get("type") else ""
            desc = f" — {md_escape(v['desc'])}" if v.get("desc") else ""
            L.append(f"- **{name}**{kind}{desc}")
        L.append("")

    L += ["## Related Lists", "", "Other curated lists that overlap with this one:", ""]
    L += [f"- [{r}](https://github.com/{r}) — {d}" for r, d in RELATED_LISTS]
    L += [
        "",
        "## Contributing",
        "",
        "Found a missing paper or a wrong link? Open an issue, or add a YAML file under "
        "[`data/`](data/) and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).",
        "",
        "## License",
        "",
        "[CC0-1.0](LICENSE) — the curation is in the public domain. "
        "Linked papers and code remain under their own licenses.",
        "",
    ]
    return "\n".join(L)


PUBLIC_FIELDS = ("id", "kind", "name", "aliases", "title", "year", "venue", "venue_detail", "category",
                 "type", "tags", "modality", "architecture", "task", "key", "links", "model_card",
                 "evaluates", "findings", "interp_method", "citation", "reviewed", "inputs", "outputs", "architecture_family", "code_status",
                 "perturbation_type", "generalization", "added", "sources", "review_basis")


def public(e, vocab):
    out = {k: e[k] for k in PUBLIC_FIELDS if k in e}
    out["status"] = status(e)
    repo = github_repo((e.get("links") or {}).get("code"))
    if repo:
        out["github"] = repo
    return out


def build_json(models, resources, venues, vocab):
    return {
        "generated": datetime.date.today().isoformat(),
        "repo": REPO,
        "counts": {"models": len(models), "resources": len(resources), "venues": len(venues)},
        "vocab": vocab,
        "models": [public(m, vocab) for m in sorted(models, key=year_sort_key)],
        "resources": [public(r, vocab) for r in sorted(resources, key=year_sort_key)],
        "venues": venues,
    }


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            links = r.get("links") or {}
            card = r.get("model_card") or {}
            row = []
            for fld in fields:
                if fld.startswith("link_"):
                    v = links.get(fld[5:], "")
                elif fld.startswith("card_"):
                    v = card.get(fld[5:], "")
                elif fld == "status":
                    v = status(r)
                else:
                    v = r.get(fld, "")
                if isinstance(v, list):
                    v = "; ".join(map(str, v))
                row.append("" if v is None else v)
            w.writerow(row)


CONFERENCES = {"NeurIPS", "ICML", "ICLR", "AAAI", "IJCAI", "KDD", "ACL", "ACM-BCB", "RECOMB", "ISMB", "WSDM", "ICDM Workshops"}
DOI = re.compile(r"10\.\d{4,9}/[^\s?#]+")
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")


def citation_authors(cit):
    """Authors from a Chicago-style citation ("Last, First, First Last, and First Last. "Title." ...").

    Best effort: returns names as "Last, First" plus whether the list was cut with "et al".
    """
    if ' "' not in (cit or ""):  # not in the usual 'Authors. "Title." Venue' form
        return [], False
    head = cit.split(' "')[0].strip().rstrip(".")
    if not head or head.startswith('"'):
        return [], False
    etal = bool(re.search(r"\bet al\.?$", head))
    head = re.sub(r",?\s*et al\.?$", "", head)
    parts = [p.strip() for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", head) if p.strip()]
    if len(parts) < 2:
        return parts, etal
    names = [f"{parts[0]}, {parts[1]}"]  # first author is written "Last, First"
    for p in parts[2:]:
        bits = p.split()
        names.append(f"{bits[-1]}, {' '.join(bits[:-1])}" if len(bits) > 1 else p)
    return names, etal


def entry_ids(e):
    links = e.get("links") or {}
    doi = arxiv = None
    for k in ("paper", "preprint"):
        u = links.get(k) or ""
        m = DOI.search(u)
        if m and not doi and "10.48550" not in m.group(0):
            doi = re.sub(r"(v\d+|\.full|\.pdf)$", "", m.group(0))
        a = ARXIV.search(u) or re.search(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", u, re.I)
        if a and not arxiv:
            arxiv = a.group(1)
    url = next((links[k] for k in ("paper", "preprint", "project", "video", "code") if links.get(k)), "")
    return doi, arxiv, url


def kind_of(e):
    """'article' | 'inproceedings' | 'preprint' | 'misc'."""
    if status(e) == "preprint":
        return "preprint"
    if e.get("venue") in CONFERENCES:
        return "inproceedings"
    if (e.get("links") or {}).get("paper") and e.get("venue"):
        return "article"
    return "misc"


def bib_escape(s):
    return str(s or "").replace("\\", "").replace("{", "").replace("}", "").replace("&", r"\&").replace("%", r"\%")


def write_bib(path, entries):
    out = []
    for e in sorted(entries, key=lambda x: x["id"]):
        doi, arxiv, url = entry_ids(e)
        kind = kind_of(e)
        names, etal = citation_authors(e.get("citation"))
        fields = [("title", "{" + bib_escape(e["title"]) + "}")]
        if names:
            # a one-word-part name without a comma is an organisation: brace it so BibTeX keeps it whole
            fields.append(("author", " and ".join(bib_escape(n) if "," in n else "{" + bib_escape(n) + "}" for n in names)
                           + (" and others" if etal else "")))
        if e.get("year"):
            fields.append(("year", str(e["year"])))
        venue = bib_escape(e.get("venue"))
        if kind == "article":
            fields.append(("journal", venue))
        elif kind == "inproceedings":
            fields.append(("booktitle", venue + (f" ({bib_escape(e['venue_detail'])})" if e.get("venue_detail") else "")))
        elif venue:
            fields.append(("howpublished", venue))
        if doi:
            fields.append(("doi", doi))
        if arxiv:
            fields += [("eprint", arxiv), ("archiveprefix", "arXiv")]
        if url:
            fields.append(("url", url))
        if e.get("tags"):
            fields.append(("keywords", ", ".join(e["tags"])))
        btype = {"article": "article", "inproceedings": "inproceedings"}.get(kind, "misc")
        out.append(f"@{btype}{{{e['id']},\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in fields) + "\n}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("% Generated by scripts/build.py from data/ — do not edit by hand.\n"
                "% Authors are parsed from each entry's citation; use the DOI to refresh full metadata.\n\n" + "\n".join(out))


def write_ris(path, entries):
    TY = {"article": "JOUR", "inproceedings": "CPAPER", "preprint": "UNPB", "misc": "GEN"}
    lines = []
    for e in sorted(entries, key=lambda x: x["id"]):
        doi, arxiv, url = entry_ids(e)
        names, _ = citation_authors(e.get("citation"))
        lines.append(f"TY  - {TY[kind_of(e)]}")
        lines.append(f"TI  - {e['title']}")
        lines += [f"AU  - {n}" for n in names]
        if e.get("year"):
            lines.append(f"PY  - {e['year']}")
        if e.get("venue"):
            lines.append(f"T2  - {e['venue']}")
        if doi:
            lines.append(f"DO  - {doi}")
        if url:
            lines.append(f"UR  - {url}")
        lines += [f"KW  - {t}" for t in e.get("tags") or []]
        if e.get("key"):
            lines.append(f"AB  - {e['key']}")
        lines.append(f"ID  - {e['id']}")
        lines.append("ER  - \n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    vocab = load_vocab()
    models, resources, venues = load_entries("models"), load_entries("resources"), load_venues()

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write(build_readme(models, resources, venues, vocab))

    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "data.json"), "w", encoding="utf-8") as f:
        json.dump(build_json(models, resources, venues, vocab), f, ensure_ascii=False, indent=1)

    os.makedirs(os.path.join(ROOT, "exports"), exist_ok=True)
    links = ["link_" + k for k in ("paper", "preprint", "code", "weights", "project", "dataset", "docs", "video")]
    write_csv(os.path.join(ROOT, "exports", "models.csv"), sorted(models, key=year_sort_key),
              ["id", "name", "aliases", "title", "year", "venue", "venue_detail", "status", "category", "tags",
               "modality", "architecture", "architecture_family", "inputs", "outputs", "perturbation_type",
               "generalization", "task", "key", *links, "code_status",
               *["card_" + k for k in vocab["model_card_fields"]],
               "citation", "added", "review_basis", "reviewed"])
    write_csv(os.path.join(ROOT, "exports", "resources.csv"), sorted(resources, key=year_sort_key),
              ["id", "type", "title", "aliases", "year", "venue", "venue_detail", "status", "tags", "key",
               "evaluates", "findings", "interp_method", *links, "citation", "added", "review_basis", "reviewed"])
    write_bib(os.path.join(ROOT, "exports", "catalogue.bib"), models + resources)
    write_ris(os.path.join(ROOT, "exports", "catalogue.ris"), models + resources)

    print(f"Built README.md, docs/data.json, exports/: {len(models)} models, "
          f"{len(resources)} resources, {len(venues)} venues.")


if __name__ == "__main__":
    main()
