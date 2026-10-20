#!/usr/bin/env python3
"""Verify entries against OpenAlex, Crossref, arXiv, bioRxiv and OpenReview.

    python scripts/verify.py                     # all entries -> reports/verification.{md,json}
    python scripts/verify.py --only scgpt,uce    # a few entries (report is marked partial)
    python scripts/verify.py --no-links          # skip the dead-link check
    python scripts/verify.py --refresh           # ignore cached responses in .cache/verify/
    python scripts/verify.py --apply             # apply the safe fixes in reports/verification.json

Set VERIFY_MAILTO to a contact address for the OpenAlex/Crossref polite pool, and
VERIFY_OPENALEX_KEY to a (free) OpenAlex API key: without a key OpenAlex only allows
a small daily budget shared by everyone on the same IP address.

Nothing in data/ changes unless --apply is given, and --apply only applies
suggestions marked `safe`: venue/year from a DOI-matched record on which
Crossref and OpenAlex agree, and the paper/preprint split when the preprint
server or Crossref names exactly one published DOI. Everything else is for a human.
"""
import argparse
import datetime
import difflib
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from urllib.parse import quote, unquote, urlparse

import requests

from catalog import PREPRINT_VENUES, ROOT, load_entries, load_yaml, utf8_stdout, write_yaml

CACHE = os.path.join(ROOT, ".cache", "verify")
REPORT_MD = os.path.join(ROOT, "reports", "verification.md")
REPORT_JSON = os.path.join(ROOT, "reports", "verification.json")
RATE = 5.0                                   # requests per second, overall
HOST_GAP = {"export.arxiv.org": 3.0}         # arXiv asks for one request every 3 s
RETRIES = 4
TITLE_OK = 0.9                               # below this a title is flagged
SEARCH_OK = 0.93                             # title-search hits must be at least this close
FIELD_ORDER = ["id", "kind", "type", "name", "aliases", "title", "year", "venue", "venue_detail", "category",
               "tags", "modality", "architecture", "task", "key", "links", "evaluates", "model_card",
               "citation", "reviewed", "review_notes"]
LINK_ORDER = ["paper", "preprint", "code", "weights", "project", "dataset", "docs", "video"]

# Issue types, most important first (also the report's section order).
ISSUES = OrderedDict([
    ("published_version", "Preprint now published"),
    ("venue_mismatch", "Venue mismatch"),
    ("year_mismatch", "Year mismatch"),
    ("missing_value", "Missing venue/year that a source knows"),
    ("title_mismatch", "Title mismatch"),
    ("found_by_title", "Paper found by title search (no usable identifier in links)"),
    ("venue_unconfirmed", "Venue not confirmed by any source"),
    ("not_found", "Identifier not found in any source"),
    ("no_identifier", "No identifier and no title-search match"),
    ("dead_link", "Dead link"),
    ("link_unchecked", "Link blocked automated checking (401/403/429)"),
])

VENUE_PATTERNS = [
    (r"neural information processing systems|^neurips", "NeurIPS"),
    (r"international conference on machine learning|^icml", "ICML"),
    (r"international conference on learning representations|^iclr", "ICLR"),
    (r"aaai conference on artificial intelligence|^aaai", "AAAI"),
    (r"web search and data mining|^wsdm", "WSDM"),
    (r"association for computational linguistics", "ACL"),
    (r"conference on data mining workshops", "ICDM Workshops"),
    (r"proceedings of the national academy of sciences", "PNAS"),
    (r"^biorxiv", "bioRxiv"), (r"^medrxiv", "medRxiv"), (r"^arxiv", "arXiv"),
    (r"^research square", "Research Square"), (r"^ssrn", "SSRN"),
]
# Containers that don't name the venue (PMLR hosts ICML and others; LNCS hosts many).
VAGUE_VENUES = {"proceedings of machine learning research", "lecture notes in computer science"}

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s?#]+)")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[a-z]{2})?/\d{7})(?:v\d+)?", re.I)
OPENREVIEW_RE = re.compile(r"openreview\.net/(?:forum|pdf)\?id=([\w-]+)")
NATURE_RE = re.compile(r"nature\.com/articles/([a-z0-9.\-]+)", re.I)
BIORXIV_PREFIXES = ("10.1101/", "10.64898/")    # bioRxiv/medRxiv moved to 10.64898 in late 2025


# ---------------------------------------------------------------- HTTP

class BudgetExhausted(Exception):
    """An API refused further requests for the day; re-run later (the cache keeps progress)."""


class Http:
    """GET/HEAD with a disk cache, a global rate limit and retries on 429/5xx."""

    def __init__(self, mailto, refresh=False, openalex_key=""):
        self.s = requests.Session()
        contact = f"; mailto:{mailto}" if mailto else ""
        self.s.headers["User-Agent"] = (
            f"scfm-catalogue-verify/1.0 (+https://github.com/MohammadUsman0/single-cell-foundation-models{contact})")
        self.mailto, self.refresh, self.openalex_key = mailto, refresh, openalex_key
        self.last, self.host_last = 0.0, {}
        self.stats = Counter()

    def _wait(self, host):
        t = max(self.last + 1.0 / RATE, self.host_last.get(host, 0.0) + HOST_GAP.get(host, 0.0))
        if t > time.monotonic():
            time.sleep(t - time.monotonic())
        self.last = self.host_last[host] = time.monotonic()

    def fetch(self, url, params=None, kind="json", method="GET", retries=RETRIES, timeout=30):
        """Return (status, body). body is parsed JSON, text, or None for kind="status".
        status is None when the host could not be reached at all."""
        key = hashlib.sha1(json.dumps([method, kind, url, params], sort_keys=True).encode()).hexdigest()
        path = os.path.join(CACHE, key[:2], key + ".json")
        if not self.refresh and os.path.exists(path):
            self.stats["cached"] += 1
            with open(path, encoding="utf-8") as f:
                c = json.load(f)
            return c["status"], c["body"]

        host = urlparse(url).netloc
        p = dict(params or {})
        if self.mailto and host in ("api.openalex.org", "api.crossref.org"):
            p["mailto"] = self.mailto
        if self.openalex_key and host == "api.openalex.org":
            p["api_key"] = self.openalex_key
        status, body = None, None
        for attempt in range(retries):
            if attempt:
                self.stats["retries"] += 1
                print(f"    retry {attempt} {method} {url} (last: {status or body})", file=sys.stderr, flush=True)
            self._wait(host)
            self.stats["requests"] += 1
            t0 = time.monotonic()
            try:
                r = self.s.request(method, url, params=p or None, timeout=timeout, allow_redirects=True,
                                   stream=(kind == "status"))
            except requests.RequestException as ex:
                status, body = None, type(ex).__name__
                print(f"    {body} after {time.monotonic() - t0:.0f}s: {url}", file=sys.stderr, flush=True)
                if attempt + 1 < retries:
                    time.sleep(2 ** attempt)
                continue
            status = r.status_code
            if status == 429 or status >= 500:
                ra = r.headers.get("Retry-After", "")
                r.close()
                if status == 429 and ra.isdigit() and int(ra) > 600:
                    raise BudgetExhausted(f"{host} refused requests for {int(ra) // 3600}h{int(ra) % 3600 // 60:02d}m "
                                          f"(daily budget used up)")
                if attempt + 1 < retries:
                    time.sleep(min(int(ra) if ra.isdigit() else 2 ** (attempt + 1), 60))
                continue
            if kind == "status":
                body = r.url
                r.close()
            elif kind == "json":
                try:
                    body = r.json() if status == 200 else None
                except ValueError:
                    body = None
            else:
                body = r.text if status == 200 else None
            break
        # Don't cache transient failures, so the next run tries again.
        if status is not None and status != 429 and status < 500:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"url": url, "params": params, "status": status, "body": body}, f)
        return status, body


# ---------------------------------------------------------------- helpers

def norm_title(t):
    t = re.sub(r"<[^>]+>", " ", html.unescape(t or ""))
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def title_ratio(a, b):
    a, b = norm_title(a), norm_title(b)
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 3) if a and b else 0.0


def clean_doi(d):
    d = unquote(d).strip().rstrip(".")
    d = re.sub(r"(\.full(\.pdf)?(\+html)?|\.abstract|\.pdf|/full|/abstract|/pdf|/meta|/epdf)$", "", d, flags=re.I)
    if d.lower().startswith(BIORXIV_PREFIXES):
        d = re.sub(r"v\d+$", "", d)
    return d.lower()


def canon_venue(name, known):
    """Map a source's venue name onto the short names used in data/ (None if vague)."""
    if not name:
        return None
    n = re.sub(r"\s*\([^)]*\)\s*$", "", html.unescape(name)).strip()
    low = n.lower()
    if low in VAGUE_VENUES:
        return None
    for pat, short in VENUE_PATTERNS:
        if re.search(pat, low):
            return short
    for k in known:
        if k.lower() == low:
            return k
    return n


def is_preprint_venue(v):
    return bool(v) and v.lower() in PREPRINT_VENUES


def identifiers(entry):
    """Identifiers found in links.paper / links.preprint, in that order."""
    out = []
    links = entry.get("links") or {}
    for key in ("paper", "preprint"):
        url = links.get(key)
        if not url:
            continue
        i = {"link": key, "url": url}
        if m := ARXIV_RE.search(url):
            i["arxiv"] = m.group(1)
        elif m := OPENREVIEW_RE.search(url):
            i["openreview"] = m.group(1)
        elif m := DOI_RE.search(url):
            i["doi"] = clean_doi(m.group(1))
        elif m := NATURE_RE.search(url):
            i["doi"] = clean_doi("10.1038/" + m.group(1))
        out.append(i)
    return out


# ---------------------------------------------------------------- sources
# Each returns a "record": {source, id, title, year, venue, preprint, url} or None.

def crossref(http, doi, known):
    st, body = http.fetch(f"https://api.crossref.org/works/{quote(doi, safe='/:')}")
    if st != 200 or not body:
        return None
    m = body.get("message") or {}
    title = (m.get("title") or [""])[0]
    sub = (m.get("subtitle") or [""])[0]
    if sub and norm_title(sub) not in norm_title(title):
        title = f"{title}: {sub}"
    def year_of(k):
        parts = (m.get(k) or {}).get("date-parts") or [[None]]
        return parts[0][0] if parts[0] else None
    year = next((y for y in map(year_of, ("published", "issued", "posted", "created")) if y), None)
    # `published` is the earliest of online/print, which is the catalogue's convention
    # (CONTRIBUTING.md). A DOI registered a year or more after that date suggests a back-dated issue.
    created = year_of("created")
    year_note = ""
    if year and created and created - year >= 1:
        year_note = f"DOI record created {created}, after the claimed {year}: publisher date may be back-dated"
    preprint = m.get("type") == "posted-content"
    venue = (m.get("container-title") or [None])[0]
    if preprint:
        venue = (m.get("institution") or [{}])[0].get("name") or ("bioRxiv" if doi.startswith(BIORXIV_PREFIXES) else None)
    rel = m.get("relation") or {}
    published = [r["id"].lower() for r in rel.get("is-preprint-of", []) if r.get("id-type") == "doi"]
    return {"source": "crossref", "id": doi, "title": title, "year": year, "venue": canon_venue(venue, known),
            "preprint": preprint, "url": f"https://doi.org/{doi}", "published_dois": published, "year_note": year_note}


OA_SELECT = "id,doi,title,publication_year,type,primary_location,locations"


def _oa_record(w, known):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    venue = canon_venue(src.get("display_name"), known) if src.get("type") in ("journal", "conference") or \
        is_preprint_venue(canon_venue(src.get("display_name"), known)) else None
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
    preprint = w.get("type") == "preprint" or is_preprint_venue(venue)
    published = []
    for l in w.get("locations") or []:
        s = l.get("source") or {}
        v = canon_venue(s.get("display_name"), known)
        if s.get("type") in ("journal", "conference") and v and not is_preprint_venue(v):
            m = DOI_RE.search(l.get("landing_page_url") or "")
            if m:
                published.append(clean_doi(m.group(1)))
    return {"source": "openalex", "id": doi or w.get("id"), "openalex": w.get("id"), "title": w.get("title"),
            "year": w.get("publication_year"), "venue": venue, "preprint": preprint,
            "url": f"https://doi.org/{doi}" if doi else w.get("id"),
            "published_dois": sorted(set(published) - {doi})}


def openalex_doi(http, doi, known):
    st, body = http.fetch(f"https://api.openalex.org/works/doi:{quote(doi, safe='/:')}", {"select": OA_SELECT})
    return _oa_record(body, known) if st == 200 and body else None


def openalex_search(http, title, known):
    """Records for the top title-search hits, closest first."""
    q = re.sub(r"[,:;!?|()\[\]]", " ", title or "")
    st, body = http.fetch("https://api.openalex.org/works", {"search": q, "per_page": 8, "select": OA_SELECT})
    if st != 200 or not body:
        return []
    out = []
    for w in body.get("results") or []:
        r = _oa_record(w, known)
        r["ratio"] = title_ratio(title, r["title"])
        out.append(r)
    return sorted(out, key=lambda r: -r["ratio"])


def arxiv(http, aid):
    st, text = http.fetch("http://export.arxiv.org/api/query", {"id_list": aid}, kind="text")
    if st != 200 or not text:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    try:
        e = ET.fromstring(text).find("a:entry", ns)
    except ET.ParseError:
        return None
    if e is None or "api/errors" in (e.findtext("a:id", "", ns)):
        return None
    pub_doi = (e.findtext("x:doi", "", ns) or "").strip().lower()
    return {"source": "arxiv", "id": aid, "title": " ".join(e.findtext("a:title", "", ns).split()),
            "year": int(e.findtext("a:published", "0000", ns)[:4]) or None, "venue": "arXiv", "preprint": True,
            "url": f"https://arxiv.org/abs/{aid}", "journal_ref": (e.findtext("x:journal_ref", "", ns) or "").strip(),
            "published_dois": [clean_doi(pub_doi)] if pub_doi else []}


def biorxiv(http, doi, server):
    for srv in [server] + [s for s in ("biorxiv", "medrxiv") if s != server]:
        st, body = http.fetch(f"https://api.biorxiv.org/details/{srv}/{doi}")
        coll = (body or {}).get("collection") or []
        if st == 200 and coll:
            first, last = coll[0], coll[-1]
            pub = {clean_doi(v["published"]) for v in coll if v.get("published") and v["published"] != "NA"}
            return {"source": srv, "id": doi, "title": last.get("title"), "year": int(first["date"][:4]),
                    "venue": "medRxiv" if srv == "medrxiv" else "bioRxiv", "preprint": True,
                    "url": f"https://doi.org/{doi}", "published_dois": sorted(pub)}
    return None


def openreview(http, nid, known):
    for base in ("https://api2.openreview.net", "https://api.openreview.net"):
        st, body = http.fetch(f"{base}/notes", {"id": nid})
        notes = (body or {}).get("notes") or []
        if st == 200 and notes:
            c = notes[0].get("content") or {}
            val = lambda k: (c.get(k) or {}).get("value") if isinstance(c.get(k), dict) else c.get(k)
            vstr = val("venue") or ""
            m = re.search(r"(\d{4})", vstr)
            ms = notes[0].get("pdate") or notes[0].get("cdate")
            year = int(m.group(1)) if m else (datetime.datetime.utcfromtimestamp(ms / 1000).year if ms else None)
            accepted = bool(vstr) and not re.search(r"submitted to|withdrawn|rejected", vstr, re.I)
            return {"source": "openreview", "id": nid, "title": val("title"), "year": year,
                    "venue": canon_venue(re.sub(r"\s+\d{4}.*$", "", vstr), known) if accepted else None,
                    "venue_string": vstr, "accepted": accepted, "preprint": not accepted,
                    "url": f"https://openreview.net/forum?id={nid}", "published_dois": []}
    return None


# ---------------------------------------------------------------- per entry

def issue(kind, current=None, suggested=None, source="", note="", safe=False, changes=None):
    return {"type": kind, "current": current, "suggested": suggested, "source": source, "note": note,
            "safe": safe, "changes": changes or {}}


def fmt_ver(venue, year):
    return " ".join(str(x) for x in (venue, year) if x) or "—"


def published_record(http, dois, known):
    """Crossref + OpenAlex for the one published DOI; None if none or ambiguous."""
    if len(dois) != 1:
        return None, None
    return crossref(http, dois[0], known), openalex_doi(http, dois[0], known)


def verify_entry(http, e, known):
    title, year, venue = e.get("title") or "", e.get("year"), e.get("venue")
    links = e.get("links") or {}
    ids = identifiers(e)
    res = {"id": e["id"], "file": e["_file"], "kind": e["kind"], "match": None,
           "identifiers": ids, "records": [], "issues": []}
    add = res["issues"].append

    # 1. records for the linked identifier
    linked, second, ident = None, None, None
    for i in ids:
        if "arxiv" in i:
            linked = arxiv(http, i["arxiv"])
            second = openalex_doi(http, f"10.48550/arxiv.{i['arxiv']}", known)
            res["match"] = "arxiv"
        elif "openreview" in i:
            linked = openreview(http, i["openreview"], known)
            res["match"] = "openreview"
        elif "doi" in i and i["doi"].startswith(BIORXIV_PREFIXES):
            linked = biorxiv(http, i["doi"], "medrxiv" if "medrxiv" in i["url"] else "biorxiv")
            second = crossref(http, i["doi"], known)
            res["match"] = "doi"
        elif "doi" in i:
            linked = crossref(http, i["doi"], known)
            second = openalex_doi(http, i["doi"], known)
            res["match"] = "doi"
        if res["match"]:
            ident = i
            if not linked and second:
                linked, second = second, None
            break

    # 2. no identifier (or nothing found for it): search OpenAlex by title
    hits = []
    if not linked and title:
        hits = [h for h in openalex_search(http, title, known) if h["ratio"] >= SEARCH_OK]
        if hits:
            # Prefer the published version as "the" record; keep the preprint for the split.
            hits.sort(key=lambda h: (h["preprint"], -h["ratio"]))
            linked = hits[0]
            res["match"] = res["match"] or "title"
            if res["match"] != "title":
                res["match"] += "+title"
    if not linked:
        if ident:
            add(issue("not_found", current=ident.get("doi") or ident.get("arxiv") or ident.get("openreview"),
                      note="identifier from links." + ident["link"] + "; no source returned a record"))
        else:
            add(issue("no_identifier", current=links.get("paper"),
                      note="no DOI/arXiv/OpenReview id in links; OpenAlex title search found no close match"))
        return res

    res["records"] = [r for r in (linked, second) if r]
    src = f"{linked['source']} {linked['id']}"
    agree = lambda f: second is None or second.get(f) is None or second.get(f) == linked.get(f)

    # 3. title
    r = title_ratio(title, linked["title"])
    if r < TITLE_OK:
        add(issue("title_mismatch", current=title, suggested=linked["title"], source=src, note=f"ratio {r}"))

    if res["match"] == "title":
        others = [h for h in hits if h is not linked]
        pre = next((h for h in others if h["preprint"]), None)
        sug = {"paper": linked["url"]} | ({"preprint": pre["url"]} if pre and not linked["preprint"] else {})
        note = "found by OpenAlex title search; check it is the same paper before adding"
        if links.get("paper"):
            note += f"; current links.paper ({links['paper']}) has no DOI/arXiv id"
        add(issue("found_by_title", current=links.get("paper"), suggested=", ".join(f"{k}: {v}" for k, v in sug.items()),
                  source=f"openalex (title ratio {linked['ratio']})", note=note))

    # 4. preprint now published?
    pub_cr = pub_oa = None
    if linked["preprint"]:
        # Preprint servers and Crossref relations are authoritative; OpenAlex locations are a hint.
        strong, dois = set(), set()
        for rec in (linked, second):
            for d in (rec or {}).get("published_dois") or []:
                if d.startswith(BIORXIV_PREFIXES + ("10.48550/",)):
                    continue
                dois.add(d)
                if rec["source"] != "openalex":
                    strong.add(d)
        strong, dois = sorted(strong), sorted(dois)
        pub_cr, pub_oa = published_record(http, strong or dois, known)
        how = "preprint server/Crossref relation" if strong else "OpenAlex locations"
        if not pub_cr and not pub_oa and len(dois) <= 1:
            cand = [h for h in openalex_search(http, title, known)
                    if h["ratio"] >= SEARCH_OK and not h["preprint"] and h["venue"]
                    and (h["year"] or 0) >= (linked["year"] or 0)]
            if cand:
                pub_oa, how = cand[0], f"OpenAlex title search (ratio {cand[0]['ratio']})"
        if len(dois) > 1 and not strong:
            add(issue("published_version", current=fmt_ver(venue, year), suggested=" or ".join(dois),
                      source=src, note="several published DOIs claimed; pick by hand"))
        pub = pub_cr or pub_oa
        if pub and pub.get("venue") and not is_preprint_venue(pub["venue"]):
            res["records"] += [x for x in (pub_cr, pub_oa) if x]
            pr = title_ratio(title, pub["title"])
            changes = {"links.paper": pub["url"]}
            if not links.get("preprint"):
                changes["links.preprint"] = links.get("paper") if ident and ident["link"] == "paper" else linked["url"]
            if pub["venue"] != venue:
                changes["venue"] = pub["venue"]
            if pub["year"] and pub["year"] != year:
                changes["year"] = pub["year"]
            safe = (bool(strong) and len(strong) == 1 and pub_cr is not None and pr >= TITLE_OK
                    and not ("year" in changes and pub_cr.get("year_note"))
                    and (pub_oa is None or (pub_oa["venue"] == pub_cr["venue"] and pub_oa["year"] == pub_cr["year"]))
                    and not links.get("preprint") and res["match"] in ("doi", "arxiv"))
            why = [] if safe else [w for w, bad in (
                ("not confirmed by the preprint server/Crossref", not strong),
                ("title changed on publication (ratio %s)" % pr, pr < TITLE_OK),
                ("Crossref and OpenAlex disagree on venue/year", pub_cr and pub_oa and
                 (pub_oa["venue"] != pub_cr["venue"] or pub_oa["year"] != pub_cr["year"])),
                ("entry already has links.preprint", bool(links.get("preprint"))),
                ((pub_cr or {}).get("year_note"), "year" in changes and bool((pub_cr or {}).get("year_note"))),
                ("entry matched by title only", res["match"] not in ("doi", "arxiv"))) if bad]
            add(issue("published_version", current=fmt_ver(venue, year) + f" · {links.get('paper') or '—'}",
                      suggested=fmt_ver(pub["venue"], pub["year"]) + f" · {pub['url']}",
                      source=f"{pub['source']} {pub['id']} via {how}", safe=safe,
                      note="; ".join(why), changes=changes))
            return res  # venue/year are covered by the suggestion above

    # 5. venue / year against the version the entry describes
    if linked["preprint"] and venue and not is_preprint_venue(venue):
        jr = linked.get("journal_ref") or linked.get("venue_string") or ""
        note = "best record is a preprint and no published version was found"
        if jr:
            note += f"; journal_ref: {jr}"
        if ident and "openreview" in ident and linked["source"] != "openreview":
            note += "; OpenReview API refused automated access (403 challenge), so its decision is unknown"
        add(issue("venue_unconfirmed", current=venue, suggested=None, source=src, note=note))
    else:
        sv, sy = linked.get("venue"), linked.get("year")
        if linked["source"] == "openreview" and not linked.get("accepted"):
            add(issue("venue_mismatch", current=venue, suggested=None, source=src,
                      note=f"OpenReview says '{linked.get('venue_string') or 'no decision'}' — not an accepted paper?"))
            sv = None
        def unsafe(field):
            """Why a venue/year fix can't be applied automatically ('' if it can)."""
            if res["match"] != "doi" or linked["source"] != "crossref":
                return f"matched by {res['match']}, not a Crossref DOI record"
            if second is None or second.get(field) is None:
                return "only Crossref has it; OpenAlex can't confirm"
            if not agree(field):
                return f"OpenAlex says {second[field]}"
            if field == "year" and linked.get("year_note"):
                return linked["year_note"]
            return f"title differs (ratio {r})" if r < TITLE_OK else ""
        if sv and venue and sv != venue:
            add(issue("venue_mismatch", current=venue, suggested=sv, source=src, safe=not unsafe("venue"),
                      note=unsafe("venue"), changes={"venue": sv}))
        elif sv and not venue:
            add(issue("missing_value", current="venue: —", suggested=f"venue: {sv}", source=src,
                      safe=not unsafe("venue"), note=unsafe("venue"), changes={"venue": sv}))
        if sy and year and sy != year:
            add(issue("year_mismatch", current=year, suggested=sy, source=src, safe=not unsafe("year"),
                      note=unsafe("year"), changes={"year": sy}))
        elif sy and not year:
            add(issue("missing_value", current="year: —", suggested=f"year: {sy}", source=src,
                      safe=not unsafe("year"), note=unsafe("year"), changes={"year": sy}))
    return res


def check_links(http, e, res):
    confirmed = {i["url"] for i in res["identifiers"]} if res["records"] and res["match"] in ("doi", "arxiv", "openreview") else set()
    for key, url in (e.get("links") or {}).items():
        if re.match(r"https?://(dx\.)?doi\.org/", url):
            st, body = http.fetch(f"https://doi.org/api/handles/{quote(clean_doi(url.split('doi.org/', 1)[1]), safe='/')}")
            st = 200 if st == 200 and (body or {}).get("responseCode") == 1 else (404 if st in (200, 404) else st)
        else:
            st, _ = http.fetch(url, kind="status", method="HEAD", retries=2, timeout=15)
            if st is None or st >= 400:
                st, _ = http.fetch(url, kind="status", retries=2, timeout=15)
        if st is not None and st < 400:
            continue
        if st in (401, 403, 429, 999):
            if url not in confirmed:
                res["issues"].append(issue("link_unchecked", current=f"{key}: {url}", note=f"HTTP {st}"))
        else:
            res["issues"].append(issue("dead_link", current=f"{key}: {url}",
                                       note="unreachable" if st is None else f"HTTP {st}"))


# ---------------------------------------------------------------- output

def cell(v):
    s = "—" if v in (None, "") else str(v)
    return s.replace("|", "\\|").replace("\n", " ")


def write_reports(results, args, mailto):
    today = datetime.date.today().isoformat()
    counts = Counter(i["type"] for r in results for i in r["issues"])
    safe = Counter(i["type"] for r in results for i in r["issues"] if i["safe"])
    matches = Counter(r["match"] or "none" for r in results)
    payload = {"generated": today, "partial": bool(args.only or args.limit), "links_checked": not args.no_links,
               "entries_checked": len(results), "polite_pool": bool(mailto), "match_counts": dict(matches),
               "issue_counts": dict(counts), "entries": {r["id"]: r for r in results}}
    os.makedirs(os.path.dirname(REPORT_JSON), exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)

    L = ["# Verification report", "",
         f"Generated by `scripts/verify.py` on {today}. Do not edit by hand. "
         "Machine-readable version: [`verification.json`](verification.json).", ""]
    if payload["partial"]:
        L += [f"> **Partial run** ({len(results)} entries). Re-run without `--only`/`--limit` for the full report.", ""]
    if args.no_links:
        L += ["> Links were not checked (`--no-links`).", ""]
    L += [f"- **{len(results)}** entries checked. Matched by: "
          + ", ".join(f"{k} {v}" for k, v in sorted(matches.items(), key=lambda kv: -kv[1])) + ".",
          f"- **{sum(counts.values())}** findings in **{sum(1 for r in results if r['issues'])}** entries; "
          f"**{sum(safe.values())}** are safe fixes that `--apply` would make.",
          "- Sources: OpenAlex, Crossref, arXiv, bioRxiv/medRxiv, OpenReview. "
          "Title-search matches are never applied automatically.", "",
          "## Summary", "", "| Issue | Entries | Safe fixes |", "|---|---|---|"]
    for k, label in ISSUES.items():
        if counts[k]:
            L.append(f"| [{label}](#{k.replace('_', '-')}) | {counts[k]} | {safe[k] or ''} |")
    for k, label in ISSUES.items():
        rows = [(r, i) for r in results for i in r["issues"] if i["type"] == k]
        if not rows:
            continue
        L += ["", f"<a id=\"{k.replace('_', '-')}\"></a>", f"## {label} ({len(rows)})", "",
              "| Entry | Current | Suggested | Source | Safe | Note |", "|---|---|---|---|---|---|"]
        for r, i in sorted(rows, key=lambda x: (not x[1]["safe"], x[0]["id"])):
            L.append(f"| [`{r['id']}`](../{r['file']}) | {cell(i['current'])} | {cell(i['suggested'])} | "
                     f"{cell(i['source'])} | {'yes' if i['safe'] else ''} | {cell(i['note'])} |")
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- --apply

def put(d, key, value, order):
    """Set d[key], keeping existing key order; a new key goes after its nearest predecessor in `order`."""
    if key in d or key not in order:
        d[key] = value
        return d
    before = [k for k in order[: order.index(key)] if k in d]
    out = OrderedDict()
    if not before:
        out[key] = value
    for k, v in d.items():
        out[k] = v
        if before and k == before[-1]:
            out[key] = value
    return out


def get_field(entry, field):
    if field.startswith("links."):
        return (entry.get("links") or {}).get(field[6:])
    return entry.get(field)


def apply_fixes(only):
    with open(REPORT_JSON, encoding="utf-8") as f:
        report = json.load(f)
    applied, skipped = 0, 0
    for eid, r in report["entries"].items():
        if only and eid not in only:
            continue
        fixes = [i for i in r["issues"] if i["safe"] and i["changes"]]
        if not fixes:
            continue
        path = os.path.join(ROOT, r["file"])
        data = load_yaml(path)
        orig = json.dumps(data, sort_keys=True, default=str)
        for i in fixes:
            # Skip anything changed by hand since the report was written.
            stale = [k for k, v in i["was"].items() if get_field(data, k) != v]
            if stale:
                skipped += 1
                print(f"skip   {eid}: {', '.join(stale)} changed since the report was written")
                continue
            for k, v in i["changes"].items():
                if k.startswith("links."):
                    data = put(data, "links", put(OrderedDict(data.get("links") or {}), k[6:], v, LINK_ORDER),
                               FIELD_ORDER)
                else:
                    data = put(data, k, v, FIELD_ORDER)
            applied += 1
            print(f"apply  {eid}: " + ", ".join(f"{k} → {v}" for k, v in i["changes"].items()))
        if json.dumps(data, sort_keys=True, default=str) != orig:
            write_yaml(path, OrderedDict(data))
    print(f"{applied} fixes applied, {skipped} skipped.")
    if applied:
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check.py"), "--quiet"], check=False)
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build.py")], check=False)
    return 0


# ---------------------------------------------------------------- main

def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", help="comma-separated entry ids")
    ap.add_argument("--limit", type=int, help="check only the first N entries")
    ap.add_argument("--no-links", action="store_true", help="skip the dead-link check")
    ap.add_argument("--refresh", action="store_true", help="ignore cached responses")
    ap.add_argument("--apply", action="store_true", help="apply safe fixes from reports/verification.json")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    if args.apply:
        return apply_fixes(only)

    mailto = os.environ.get("VERIFY_MAILTO", "").strip()
    if not mailto:
        print("warning: VERIFY_MAILTO is not set; using the OpenAlex/Crossref common pool (slower).")
    entries = load_entries("models") + load_entries("resources")
    known = {e["venue"] for e in entries if e.get("venue")}
    if only:
        missing = only - {e["id"] for e in entries}
        if missing:
            print("unknown ids: " + ", ".join(sorted(missing)))
            return 1
        entries = [e for e in entries if e["id"] in only]
    if args.limit:
        entries = entries[: args.limit]

    openalex_key = os.environ.get("VERIFY_OPENALEX_KEY", "").strip()
    if not openalex_key:
        print("warning: VERIFY_OPENALEX_KEY is not set; OpenAlex allows only a small shared daily budget.")
    http = Http(mailto, refresh=args.refresh, openalex_key=openalex_key)
    results = []
    for n, e in enumerate(entries, 1):
        try:
            res = verify_entry(http, e, known)
            if not args.no_links:
                check_links(http, e, res)
        except BudgetExhausted as ex:
            print(f"stopped at {e['id']} ({n}/{len(entries)}): {ex}. No report written; "
                  "re-run later or with an API key — cached responses are kept.")
            return 2
        for i in res["issues"]:
            i["was"] = {k: get_field(e, k) for k in i["changes"]}
        results.append(res)
        tags = ", ".join(i["type"] + ("*" if i["safe"] else "") for i in res["issues"]) or "ok"
        print(f"[{n}/{len(entries)}] {e['id']} ({res['match'] or 'no match'}): {tags}", flush=True)
    write_reports(results, args, mailto)
    print(f"{sum(len(r['issues']) for r in results)} findings → reports/verification.md "
          f"({http.stats['requests']} requests, {http.stats['retries']} retries, {http.stats['cached']} cached)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
