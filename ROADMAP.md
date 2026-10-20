# Roadmap

Plan and decisions for turning this list into a **single-cell foundation model
catalogue**. Read this together with [CLAUDE.md](CLAUDE.md) (rules and layout)
and [`reports/data-quality.md`](reports/data-quality.md) (what currently needs fixing).

Status: **phase 1 done** (PR #1). **Phase 2a done** (`scripts/verify.py`,
`verify.yml`; branch `phase-2/verify`). Next: **phase 2b** cleanup.

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
8. **Our edge over Awesome-Virtual-Cell is model facts, not coverage** (agreed
   2026-10-20). Compared on 2026-10-20: they list 396 papers with a DOI, status,
   code status and evidence on every entry, a faceted live site and automated
   publication tracking; 115 of our 182 models are also in their list. They have no
   model facts (size, pretraining data, weights, license), no benchmark → model
   verdicts and no lineage. So: finish verification first, then put effort into
   model cards, the benchmark matrix and lineage, not into growing the paper count.
9. **`year` = first appearance, online-first** (agreed 2026-10-20). Matches Crossref
   `published` and OpenAlex `publication_year`, so it can be verified automatically;
   journal issue years are often missing from Crossref. Rule is in CLAUDE.md.
10. **Verification reports are not committed** (agreed 2026-10-20). They need the
    network and API keys, so they can't be rebuilt on every push and would go stale.
    `verify.yml` uploads them as an artifact and keeps a GitHub issue (label
    `verification`) up to date; phase 2b PRs quote the relevant findings.

---

## Phase 1 — restructure (done)

YAML data, `vocab.yaml`, `build.py`, `check.py`, `new_entry.py`, workflow, new
README. Migration changes are in [`reports/migration-log.md`](reports/migration-log.md).

---

## Phase 2 — verify and clean the existing entries

### 2a. `scripts/verify.py` (done)

First full run, 2026-10-20: 303 entries, 242 findings in 181 entries, 17 safe
fixes. Highlights: scGPT, scFoundation and Nicheformer are *Nature Methods*;
UCE (*Nature*), STATE (*Cell*), Novae (*Nature Methods*) and others are now
published; scCello and Tabula are NeurIPS, not *Cell*; 85 of the 87 entries
without a paper link have an exact title match; PhenoProfiler's DOI doesn't exist.

Spec as agreed:

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

Implementation notes (learned while building it):
- **OpenReview's API now answers anonymous requests with a 403 browser challenge**
  (v1 and v2). OpenReview entries fall back to an OpenAlex title search, and the
  report says when an accept/reject decision could not be checked.
- **bioRxiv/medRxiv moved to the DOI prefix `10.64898`** in late 2025; both
  `10.1101` and `10.64898` are treated as preprint-server DOIs.
- **OpenAlex now needs an API key** for real use: without one, requests draw on a
  small free daily budget shared by everyone on the same IP address (a title search
  costs 10× a lookup), and `mailto` no longer helps. Keys are free; the script reads
  `VERIFY_OPENALEX_KEY` and stops cleanly (no report, cache kept) when a daily
  budget runs out, rather than reporting unchecked entries as "not found".
- The workflow needs the repository secrets `VERIFY_MAILTO` and `VERIFY_OPENALEX_KEY`.

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

**Schema additions** (agreed 2026-10-20; add to `check.py`/`vocab.yaml` before
filling data, so the cleanup records them as it goes):
- `sources:` — URLs each fact was checked against (e.g. the DOI and Crossref
  record), and `review_basis:` — `paper`, `abstract`, `repo` or `metadata`.
  Stronger than a bare `reviewed: true`.
- `code_status:` — `linked`, `none-found` (searched, nothing), `release-pending`,
  `not-checked`. Lets `check.py` stop warning about code once someone has looked.
- `added:` — date the entry was added (powers "New this month"; cheaper now than
  reconstructing from git history later).
- Perturbation facets for perturbation/virtual-cell models: perturbation type
  (genetic, chemical, combination) and generalization regime (unseen perturbation,
  unseen context, cross-dataset, cross-species, zero-shot).
- `build.py --check` in CI: fail if generated files are out of date.
- **What a model takes and gives** (agreed 2026-10-20), as normal model fields
  (not in `model_card`, so they apply to all models), with values from
  controlled lists in `vocab.yaml` (exact lists to be approved by the maintainer):
  - `inputs` (list) — e.g. expression profile, spatial coordinates, image, DNA
    sequence, protein sequence, text, perturbation (gene/drug), chromatin accessibility.
  - `outputs` (list) — e.g. cell embedding, gene embedding, predicted expression,
    perturbation response, cell-type labels, generated cells, gene regulatory
    network, text answer.
  - `architecture_family` (one value) — e.g. transformer encoder, transformer
    decoder, state-space/Mamba, graph neural network, VAE, diffusion, flow
    matching, fine-tuned LLM, CNN, agent system. The free-text `architecture`
    stays for detail.
  Today `modality` (94/182 filled, 56 spellings) and `architecture` (85/182, 79
  spellings) are free text and can't be filtered; there is no output field. Map
  existing values where unambiguous; leave the rest blank and flagged. `outputs`
  is filled from the papers (flagship models first, phase 4a) — never guessed.

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

Added 2026-10-20, in priority order (all generated from data, no server):
7. **Citation graph from OpenAlex** `referenced_works`: which catalogue papers
   cite each other. Real data, rebuilt automatically, and the base for the
   lineage / "mind map" view.
8. **Generated charts:** models per year by category; model size vs pretraining
   data (needs model cards); code/weights availability over time; published vs preprint.
9. **Outbound links per paper** from its DOI: Semantic Scholar, Connected Papers,
   OpenAlex (Litmaps needs a login, so secondary at most).
10. **Inputs → outputs view:** filters ("takes images", "outputs perturbation
    response"), comparison-table columns, and on each model page a small
    generated diagram: *inputs → [architecture family] → outputs*.
11. *Optional, last:* topic map from title/abstract embeddings, labelled as an
    automatic grouping (clusters can mislead; Awesome-Virtual-Cell already has a
    landscape map).

Automation rebuilds everything visible, but model cards and benchmark verdicts
always go through a human-approved PR (decision 7).

Add a short **"Start here"** section to the README: the handful of models a
newcomer should know first.

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

> Read CLAUDE.md, ROADMAP.md and reports/data-quality.md. Start phase 2b: run
> `scripts/verify.py` (with VERIFY_MAILTO and VERIFY_OPENALEX_KEY set), apply the
> safe fixes with `--apply`, then go through the remaining findings in batches,
> highest value first, showing me each batch before committing.
