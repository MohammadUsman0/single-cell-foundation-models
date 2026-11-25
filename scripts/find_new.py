#!/usr/bin/env python3
"""Find new papers that may belong in the catalogue. Read-only: never changes data/.

    python scripts/find_new.py                 # last 8 days -> reports/candidates.md
    python scripts/find_new.py --days 30       # a longer window
    python scripts/find_new.py --min-score 4   # stricter

Searches three free, keyless sources for the date window:
  bioRxiv / medRxiv   every preprint posted (relevant subject areas), via api.biorxiv.org
  arXiv               q-bio and cs.LG papers matching single-cell / virtual-cell terms
  Europe PMC          journal articles matching the same terms (preprints come from bioRxiv)

Each paper is scored on its title and abstract (single-cell context + model, benchmark or
interpretability terms), compared with the catalogue (DOI, arXiv id, title) and listed with a
suggested type and any code link found in the abstract. A human reviews the list; accepted
papers are added with new_entry.py or by hand and verified as usual (see CONTRIBUTING).
"""
import argparse
import datetime
import os
import re
import sys

from catalog import ROOT, load_entries, utf8_stdout
from verify import DOI_RE, Http, clean_doi, identifiers, norm_title, title_ratio

OUT = os.path.join(ROOT, "reports", "candidates.md")
BIORXIV_SUBJECTS = {"bioinformatics", "genomics", "systems biology", "synthetic biology", "cell biology",
                    "genetics", "immunology", "cancer biology", "developmental biology", "neuroscience"}

# A paper must mention single-cell (or virtual-cell) context ...
CONTEXT = re.compile(r"single[- ]cell|scrna|scatac|snrna|spatial (?:transcriptom|omics|proteom)|perturb-seq|"
                     r"crispr screen|virtual cell|cell painting|cell state|whole[- ]cell model", re.I)
# ... and score on what it is about (pattern, points, label). At least one CORE topic is required;
# the others only add points, so generic method papers don't pass on "benchmark" + "we propose".
TOPICS = [
    (r"foundation model", 3, "foundation model"),
    (r"virtual cells?\b|world model[^.]{0,80}cell|cell[^.]{0,80}world model|digital twin", 3, "virtual cell"),
    (r"perturbation (?:response|effect|prediction|model)|predict\w* (?:\w+ ){0,3}(?:responses?|effects?) (?:to|of) (?:\w+ ){0,2}perturbation", 2, "perturbation"),
    (r"interpretab|sparse autoencoder|mechanistic interpretability|probing (?:classifier|analysis)|feature attribution", 2, "interpretability"),
    (r"large language model|\bllm\b|\bagent(?:s|ic)?\b", 2, "LLM / agent"),
    (r"benchmark|systematic evaluation|we evaluate", 2, "benchmark"),
    (r"pre-?train|transformer|self-supervised|diffusion model|flow matching", 1, "deep model"),
    (r"we (?:present|introduce|propose|develop)", 1, "new method"),
]
CORE = {"foundation model", "virtual cell", "perturbation", "interpretability", "LLM / agent"}
GITHUB = re.compile(r"https?://(?:www\.)?(?:github\.com|huggingface\.co)/[\w.-]+/[\w.-]+", re.I)


def score(text):
    pts, why = 0, []
    for pat, p, label in TOPICS:
        if re.search(pat, text, re.I):
            pts += p
            why.append(label)
    return (pts if CORE & set(why) else 0), why


def suggested_type(title, text):
    t = title.lower()
    if re.search(r"\breview\b|survey|perspective|roadmap", t):
        return "survey / perspective"
    if re.search(r"benchmark|evaluat|comparison|assessment|pitfall|revisit|audit", t):
        return "benchmark"
    if re.search(r"sparse autoencoder|mechanistic interpretability|what do .{0,40} (?:learn|know)|probing|inside (?:single-cell )?foundation", text, re.I):
        return "interpretability"
    if re.search(r"opportunities|challenges", t):
        return "survey / perspective"
    if re.search(r"\bagent(?:s|ic)?\b", text, re.I):
        return "agent"
    if re.search(r"atlas|dataset|resource|compendium|catalog", t):
        return "dataset"
    return "model"


# ---------------------------------------------------------------- sources

def from_biorxiv(http, server, start, end):
    out, cursor, total = [], 0, None
    while total is None or cursor < total:
        st, body = http.fetch(f"https://api.biorxiv.org/details/{server}/{start}/{end}/{cursor}/json")
        if st != 200 or not body:
            print(f"  {server}: stopped at {cursor} (status {st})", file=sys.stderr)
            break
        msg = (body.get("messages") or [{}])[0]
        total = int(msg.get("total", msg.get("count", 0)) or 0)
        coll = body.get("collection") or []
        if not coll:
            break
        for p in coll:
            if server == "biorxiv" and p.get("category", "").lower() not in BIORXIV_SUBJECTS:
                continue
            out.append({"title": p.get("title", ""), "abstract": p.get("abstract", ""), "doi": clean_doi(p.get("doi", "")),
                        "date": p.get("date", ""), "venue": "bioRxiv" if server == "biorxiv" else "medRxiv",
                        "url": f"https://doi.org/{p.get('doi', '')}"})
        cursor += len(coll)
    return out


def from_arxiv(http, start):
    q = ("(cat:q-bio.GN OR cat:q-bio.QM OR cat:q-bio.CB OR cat:q-bio.MN OR cat:cs.LG) AND "
         '(abs:"single-cell" OR abs:"single cell" OR abs:"virtual cell" OR abs:"perturb-seq" OR abs:"spatial transcriptomics")')
    out = []
    for offset in range(0, 600, 200):
        st, text = http.fetch("https://export.arxiv.org/api/query", kind="text", params={
            "search_query": q, "sortBy": "submittedDate", "sortOrder": "descending", "start": offset, "max_results": 200})
        if st != 200 or not text:
            break
        entries = re.findall(r"<entry>(.*?)</entry>", text, re.S)
        for e in entries:
            date = re.search(r"<published>(\d{4}-\d{2}-\d{2})", e).group(1)
            if date < start:
                return out
            aid = re.search(r"arxiv\.org/abs/([^<v]+)", e).group(1)
            out.append({"title": " ".join(re.search(r"<title>(.*?)</title>", e, re.S).group(1).split()),
                        "abstract": " ".join(re.search(r"<summary>(.*?)</summary>", e, re.S).group(1).split()),
                        "arxiv": aid, "date": date, "venue": "arXiv", "url": f"https://arxiv.org/abs/{aid}"})
        if len(entries) < 200:
            break
    return out


def from_europepmc(http, start, end):
    q = ('("single-cell" OR "single cell" OR "virtual cell" OR "spatial transcriptomics" OR "Perturb-seq") AND '
         '("foundation model" OR "perturbation" OR "language model" OR "benchmark" OR "transformer" OR "interpretability") '
         f"AND FIRST_PDATE:[{start} TO {end}] AND NOT SRC:PPR")
    out, cursor = [], "*"
    for _ in range(10):
        st, body = http.fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={
            "query": q, "format": "json", "resultType": "core", "pageSize": 1000, "cursorMark": cursor})
        if st != 200 or not body:
            break
        for r in body.get("resultList", {}).get("result", []):
            doi = clean_doi(r.get("doi", "")) if r.get("doi") else ""
            out.append({"title": r.get("title", "").rstrip("."), "abstract": re.sub(r"<[^>]+>", " ", r.get("abstractText", "")),
                        "doi": doi, "date": r.get("firstPublicationDate", ""), "venue": r.get("journalTitle", "") or "journal",
                        "url": f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}"})
        nxt = body.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
    return out


# ---------------------------------------------------------------- main

def known_index():
    dois, arxivs, titles = set(), set(), []
    for e in load_entries("models") + load_entries("resources"):
        for i in identifiers(e):
            dois.add(i.get("doi", "")) if i.get("doi") else arxivs.add(i.get("arxiv", ""))
        for u in e.get("sources") or []:
            if m := DOI_RE.search(u or ""):
                dois.add(clean_doi(m.group(1)))
        titles += [norm_title(t) for t in [e["title"]] + list(e.get("aliases") or []) if t]
    return dois, arxivs, set(titles), titles


def in_catalogue(p, idx):
    dois, arxivs, tset, tlist = idx
    if p.get("doi") and p["doi"] in dois or p.get("arxiv") and p["arxiv"] in arxivs:
        return True
    t = norm_title(p["title"])
    if t in tset:
        return True
    words = set(t.split())
    return any(title_ratio(t, k) >= 0.9 for k in tlist if len(words & set(k.split())) >= max(3, len(words) // 2))


def write_report(rows, start, end, counts, path):
    L = [f"# Paper candidates: {start} to {end}", "",
         "Found by `scripts/find_new.py`. Nothing here is in the catalogue yet; each paper needs the usual checks "
         "(scope, metadata, code link) before it is added. Sources searched: " +
         ", ".join(f"{k} ({v})" for k, v in counts.items()) + ".", ""]
    if not rows:
        return L + ["No new candidates in this window."]
    groups = {}
    for r in rows:
        groups.setdefault(r["type"], []).append(r)
    for g in ("model", "benchmark", "interpretability", "agent", "dataset", "survey / perspective"):
        if g not in groups:
            continue
        L += [f"## {g.capitalize()} ({len(groups[g])})", "", "| Score | Paper | Source | Date | Code | Matched |", "|---|---|---|---|---|---|"]
        for r in sorted(groups[g], key=lambda r: (-r["score"], r["date"])):
            code = " ".join(f"[repo]({c})" for c in r["code"][:2]) or "—"
            title = r["title"].replace("|", "/")
            L.append(f"| {r['score']} | [{title}]({r['url']}) | {r['venue']} | {r['date']} | {code} | {', '.join(r['why'])} |")
        L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return L


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=int, default=8, help="window length in days, ending today (default 8)")
    ap.add_argument("--min-score", type=int, default=3, help="minimum relevance score (default 3)")
    ap.add_argument("--out", default=OUT, help="markdown report path")
    args = ap.parse_args()

    end = datetime.date.today()
    start = (end - datetime.timedelta(days=args.days)).isoformat()
    end = end.isoformat()
    http = Http(os.environ.get("VERIFY_MAILTO", "").strip(), refresh=True)
    print(f"Searching {start} to {end} ...")
    papers, counts = [], {}
    for name, fn in (("bioRxiv", lambda: from_biorxiv(http, "biorxiv", start, end)),
                     ("medRxiv", lambda: from_biorxiv(http, "medrxiv", start, end)),
                     ("arXiv", lambda: from_arxiv(http, start)),
                     ("Europe PMC", lambda: from_europepmc(http, start, end))):
        got = fn()
        counts[name] = len(got)
        papers += got
        print(f"  {name}: {len(got)} papers")

    idx, seen, rows = known_index(), set(), []
    for p in papers:
        text = f"{p['title']} {p['abstract']}"
        key = p.get("doi") or p.get("arxiv") or norm_title(p["title"])
        if key in seen or not CONTEXT.search(text):
            continue
        seen.add(key)
        pts, why = score(text)
        if pts < args.min_score or in_catalogue(p, idx):
            continue
        rows.append({**p, "score": pts, "why": why, "type": suggested_type(p["title"], text),
                     "code": sorted({c.rstrip(".)") for c in GITHUB.findall(p["abstract"])})})
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    write_report(rows, start, end, counts, args.out)
    print(f"{len(rows)} candidates -> {os.path.relpath(args.out, ROOT)}")


if __name__ == "__main__":
    main()
