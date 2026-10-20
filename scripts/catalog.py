"""Shared helpers: load the catalogue from data/ and the controlled vocabulary."""
import glob
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PREPRINT_VENUES = {"arxiv", "biorxiv", "medrxiv", "research square", "chemrxiv", "ssrn", "preprints.org"}


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def utf8_stdout():
    """Print non-ASCII (→, —) without crashing on consoles that default to cp1252 (Windows)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def load_vocab():
    return load_yaml(os.path.join(DATA, "vocab.yaml"))


def load_entries(kind):
    """Return entries of one kind ("models" or "resources"), each with a `_file` key."""
    out = []
    for path in sorted(glob.glob(os.path.join(DATA, kind, "*.yaml"))):
        e = load_yaml(path) or {}
        e["_file"] = os.path.relpath(path, ROOT).replace(os.sep, "/")  # same report links on every OS
        out.append(e)
    return out


def load_venues():
    p = os.path.join(DATA, "venues.yaml")
    return load_yaml(p) or [] if os.path.exists(p) else []


def status(entry):
    v = (entry.get("venue") or "").strip().lower()
    if not v:
        return "unknown"
    return "preprint" if v in PREPRINT_VENUES else "published"


GITHUB_REPO = re.compile(r"^https?://github\.com/([^/\s]+)/([^/\s#?]+)")


def github_repo(url):
    """'https://github.com/owner/repo/tree/x' -> 'owner/repo', else None."""
    m = GITHUB_REPO.match(url or "")
    if not m:
        return None
    repo = m.group(2)
    return f"{m.group(1)}/{repo[:-4] if repo.endswith('.git') else repo}"


def slug(text, max_words=6):
    import unicodedata
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    words = re.sub(r"[^a-zA-Z0-9]+", " ", t).strip().lower().split()
    return "-".join(words[:max_words]) or "entry"


def write_yaml(path, data):
    """Write an entry with keys in the given order (no sorting)."""
    from collections import OrderedDict

    class Dumper(yaml.SafeDumper):
        pass
    Dumper.add_representer(OrderedDict, lambda d, v: d.represent_dict(v.items()))
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100)


def year_sort_key(e):
    y = e.get("year")
    return (0 if isinstance(y, int) else 1, -(y or 0), (e.get("name") or e.get("title") or "").lower())
