#!/usr/bin/env python3
"""Build every generated file from data/.

    python scripts/build.py

Writes:
  README.md               simple tagged list (never edit by hand)
  docs/data.json          full catalogue for the GitHub Pages site
  exports/models.csv      flat CSV of models
  exports/resources.csv   flat CSV of resources
"""
import csv
import datetime
import json
import os
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
    link_md = [f"[[{k}]({links[k]})]" for k in ("paper", "code", "weights", "project") if links.get(k)]
    repo = github_repo(links.get("code"))
    if repo:
        link_md.append(f"![stars](https://img.shields.io/github/stars/{repo}?style=flat-square&label=%E2%98%85)")
    if link_md:
        parts.append(" ".join(link_md))
    return "- " + " · ".join(parts)


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
        "# Awesome Single-Cell Foundation Models & Virtual Cell Modelling "
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
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
                 "evaluates", "citation", "reviewed")


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
                else:
                    v = r.get(fld, "")
                if isinstance(v, list):
                    v = "; ".join(map(str, v))
                row.append("" if v is None else v)
            w.writerow(row)


def main():
    vocab = load_vocab()
    models, resources, venues = load_entries("models"), load_entries("resources"), load_venues()

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write(build_readme(models, resources, venues, vocab))

    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "data.json"), "w", encoding="utf-8") as f:
        json.dump(build_json(models, resources, venues, vocab), f, ensure_ascii=False, indent=1)

    os.makedirs(os.path.join(ROOT, "exports"), exist_ok=True)
    write_csv(os.path.join(ROOT, "exports", "models.csv"), sorted(models, key=year_sort_key),
              ["id", "name", "title", "year", "venue", "category", "tags", "modality", "architecture",
               "key", "link_paper", "link_code", "link_weights", "link_project", "card_params",
               "card_pretraining_cells", "card_weights", "card_license", "reviewed"])
    write_csv(os.path.join(ROOT, "exports", "resources.csv"), sorted(resources, key=year_sort_key),
              ["id", "type", "title", "year", "venue", "tags", "key", "link_paper", "link_code",
               "link_project", "evaluates", "reviewed"])

    print(f"Built README.md, docs/data.json, exports/: {len(models)} models, "
          f"{len(resources)} resources, {len(venues)} venues.")


if __name__ == "__main__":
    main()
