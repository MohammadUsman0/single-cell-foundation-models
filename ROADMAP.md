# Roadmap

Plan and decisions for turning this list into a **single-cell foundation model
catalogue**. Read this together with [CLAUDE.md](CLAUDE.md) (rules and layout)
and [`reports/data-quality.md`](reports/data-quality.md) (what currently needs fixing).

Status: **phase 1 done** (PR #1). Next: **phase 2**.

---

## Decisions already made

These were agreed with the maintainer; don't re-open them without asking.

1. **Positioning.** Not another "every virtual-cell paper" list —
   [Boom5426/Awesome-Virtual-Cell](https://github.com/Boom5426/Awesome-Virtual-Cell) already does that well.
   This repo is the **model catalogue**: for each model, the facts (parameters,
   pretraining data, tokenization), whether you can actually use it (weights,
   license, package), and what benchmarks found about it.
2. **Scope: models + resources.** Foundation models get full entries with an
   optional `model_card`. Everything else relevant (benchmarks, datasets, tools,
   surveys, perspectives, non-FM perturbation methods) is a lighter resource entry.
3. **README stays simple; a GitHub Pages site does the exploring.** README = one
   line per entry, grouped by category. Site (`docs/`) = search, filters,
   comparison table, model pages, lineage graph, model × benchmark matrix.
   Both are generated from the same `data/`.
4. **One primary category + many tags.** Category decides the README section;
   tags drive filtering. All values are in `data/vocab.yaml`.
5. **Source of truth for facts = scholarly databases**, not other lists.
   OpenAlex / Crossref / arXiv / bioRxiv for title, year, venue, DOI and
   preprint → published links.
6. **Other lists are for discovery only.**
   - OmicsML/awesome-foundation-model-single-cell-papers is **MIT** — entries can
     be imported, with credit.
   - Boom5426/Awesome-Virtual-Cell has **no license** — use it to find titles,
     then look them up ourselves. Don't copy its descriptions or tags.
7. **Automation proposes, a human approves.** Scripts write reports or open
   PRs; nothing auto-merges.

---

## Phase 1 — restructure (done)

YAML data, `vocab.yaml`, `build.py`, `check.py`, `new_entry.py`, workflow, new
README. Migration changes are in [`reports/migration-log.md`](reports/migration-log.md).

---

## Phase 2 — verify and clean the existing entries

### 2a. `scripts/verify.py`

Checks every entry against external sources and **writes a report**; it does
not change `data/` unless run with `--apply` on specific safe fixes.

Inputs: all `data/models/*.yaml` and `data/resources/*.yaml`.

For each entry:
1. **Resolve an identifier** from `links.paper` / `links.preprint`:
   DOI (`10.xxxx/...`), arXiv id, bioRxiv/medRxiv DOI, OpenReview id.
   If none, search OpenAlex by title.
2. **Fetch metadata:**
   - OpenAlex `https://api.openalex.org/works/doi:<doi>` (or `?search=<title>`) →
     title, publication year, host venue, DOI, `locations` (gives preprint and
     published versions).
   - Crossref `https://api.crossref.org/works/<doi>` → container title (journal),
     `relation.is-preprint-of` / `has-preprint`.
   - arXiv `http://export.arxiv.org/api/query?id_list=<id>` → title, year, journal_ref.
   - bioRxiv `https://api.biorxiv.org/details/biorxiv/<doi>` → `published` field
     gives the journal DOI if it was published.
   - Use the OpenAlex/Crossref polite pool: set a `mailto` from an env var
     (e.g. `VERIFY_MAILTO`), never hard-code an address.
   - Cache responses in `.cache/verify/` (git-ignored) so re-runs are fast.
   - Rate-limit (≈ 5 requests/s) and retry on 429/5xx.
3. **Compare and classify:**
   - title match (normalised fuzzy ratio; flag < 0.9)
   - year mismatch
   - venue mismatch (e.g. data says `Nature`, source says `Nature Methods`)
   - **preprint now published** → suggest `links.paper` = journal URL,
     `links.preprint` = old link, update `venue`/`year`
   - no identifier found / not found anywhere
   - dead link (HEAD/GET status ≥ 400) for every URL in `links`
4. **Output** `reports/verification.md` (grouped table per issue type with
   current vs suggested values) and `reports/verification.json` (machine-readable
   suggestions).
5. `--apply` applies only unambiguous fixes from the JSON: venue/year from a
   DOI-matched record, adding `preprint`/`paper` split. Everything else is
   left for a human. After applying, run `check.py` and `build.py`.

Add a workflow `verify.yml` (manual `workflow_dispatch` + monthly schedule)
that runs `verify.py` and uploads the report as an artifact or opens an issue.

### 2b. Cleanup (driven by the two reports)

- **Wrong venues** already known: scGPT, scFoundation, Nicheformer list `Nature`
  but their citations say *Nature Methods*; 8 entries list `Cell` without a Cell link.
- **Non-models → resources**, and merge with the duplicate resource entries
  that already exist: Spatial Perturb-seq, Perturb-FISH, ProtiCelli, SubCell
  (check: SubCell may genuinely be a model — keep one entry, the right kind),
  CRISPRi Map, Comment, Stanford PhD Thesis, Theory, Cell Maps, OCTO-vc.
- **Placeholder names** (e.g. "Comment", "Theory", "scFM", "Multimodal
  foundation model") → real names from the paper.
- **Missing links**: 87 entries without a paper link, 118 models without code.
  Fill from verification results; leave blank if genuinely none.
- **Tags**: migrated tags were derived automatically and some are wrong
  (e.g. SubCell got `scRNA-seq`). Review per category.
- **`key`**: rewrite the 15 that read like copied abstract sentences and the 7
  over 300 characters.
- **Consider merging tiny categories**: `generative` (2 entries) and `other` (1).
  Ask the maintainer first.
- Set `reviewed: true` only after an entry has been checked against the paper.

Target: `check.py` warnings down to genuinely-unknown fields only.

---

## Phase 3 — GitHub Pages site

Static, no framework, no server: `docs/index.html` (+ small JS/CSS) reading
`docs/data.json`. Enable Pages: Settings → Pages → branch `main`, folder `/docs`.

Features, in priority order:
1. Search (name, title, aliases, key) and filters: category, tags (grouped by
   modality/task/approach), year range, published/preprint, has code, has
   weights, license.
2. Sortable **comparison table** of models with model-card columns.
3. **Model page** (`#/model/<id>`): all fields, links, versions/successors,
   and the benchmarks that evaluated it (from resources' `evaluates`) with verdicts.
4. Export the current filtered view as CSV / JSON / BibTeX.
5. **Model × benchmark matrix** and **lineage graph** (once phase 4 data exists).
6. "New this month" view (from git history or an `added` date field).

Must work on phone width, light and dark mode. Link it prominently at the top
of the README once live.

---

## Phase 4 — the parts no other list has

### 4a. Model cards for flagship models

Fill `model_card` (fields defined in `vocab.yaml`) for ~30 widely used models
first, verified from the paper, repo and model hub — never guessed. Starting set:
scGPT, Geneformer (+V2), scFoundation, UCE, TranscriptFormer, Nicheformer, STATE,
scBERT, CellPLM, GeneCompass, SCimilarity, scPRINT, CellFM, Tahoe-x1, C2S-Scale,
AIDO.Cell, GenePT, LangCell, scMulan, tGPT, xTrimoGene, scGPT-spatial, Novae,
EpiAgent, ChromFound, CellWhisperer, scLong, TEDDY, Cell2Sentence, SATURN.

Also add lineage: a `successor_of` / `family` field (add to vocab + check.py),
e.g. Geneformer → GeneformerV2, scGPT → scGPT-spatial, scPRINT → scPRINT-2.

### 4b. Benchmark ↔ model links

For each benchmark resource, fill `evaluates: [model ids]` and add a short
`findings` field (add to schema) such as "matched PCA on zero-shot clustering".
This powers the model pages and the matrix.

### 4c. Weekly paper finder

`scripts/find_new.py` + `find-new.yml` (weekly schedule):
- query arXiv (q-bio.GN, q-bio.QM, cs.LG), bioRxiv/medRxiv, OpenAlex for
  keywords (single-cell foundation model, scGPT, Geneformer, virtual cell,
  perturbation prediction, cell language model, …) since the last run
- de-duplicate against `data/` (title, DOI, name) and link preprint ↔ published
- score relevance; suggest kind, category and tags
- write candidates as new YAML files with `reviewed: false` on a branch and
  **open a PR** for the maintainer to accept or trim
- also refresh star counts / last-commit dates for code links

### 4d. Reuse and citation

Zenodo integration for a DOI per release; RSS/Atom feed of new entries.

---

## Prompt to start the next session

> Read CLAUDE.md, ROADMAP.md and reports/data-quality.md. Start phase 2a:
> write `scripts/verify.py` as specified in ROADMAP.md, run it, and show me the
> summary of reports/verification.md. Don't change data/ yet.
