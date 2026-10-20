# CLAUDE.md — instructions for the coding agent

Read this fully before acting. Claude Code reads this file automatically.

**Also read [ROADMAP.md](ROADMAP.md)** — agreed decisions and the detailed plan for
the remaining phases. Start there when asked to "continue".

## What this project is

An **awesome-list and model catalogue** of single-cell foundation models and AI
virtual-cell / world models, plus the benchmarks, datasets, tools, surveys,
perspectives and venues around them.

Everything is **generated** from YAML in `data/`:
- `README.md` — a simple tagged one-line-per-entry list.
- `docs/data.json` — the full catalogue for the GitHub Pages site (phase 3).
- `exports/*.csv` — flat exports.
- `reports/data-quality.md` — what `check.py` found.

Current size: ~182 models, ~121 resources, 19 venues.

## Repository layout

```
.
├── README.md                     # GENERATED — never edit by hand
├── CLAUDE.md                     # this file
├── ROADMAP.md                    # decisions + phase plan (read this next)
├── CONTRIBUTING.md               # human-facing contribution guide
├── LICENSE                       # CC0-1.0
├── data/                         # <-- SOURCE OF TRUTH
│   ├── models/<id>.yaml          # one file per model
│   ├── resources/<id>.yaml       # one file per benchmark/dataset/tool/survey/perspective/reference
│   ├── venues.yaml
│   └── vocab.yaml                # allowed categories, resource types, tags, model-card fields
├── docs/data.json                # GENERATED
├── exports/                      # GENERATED
├── reports/                      # GENERATED (data-quality.md) + migration-log.md
├── scripts/
│   ├── catalog.py                # shared loaders/helpers
│   ├── check.py                  # validates data/, writes reports/data-quality.md
│   ├── build.py                  # writes README.md, docs/data.json, exports/
│   ├── new_entry.py              # creates one YAML entry, refuses duplicates
│   └── legacy/migrate_csv.py     # one-off CSV → YAML migration (CSVs are in git history)
└── .github/workflows/build-readme.yml
```

## Golden rules

1. **`data/` is the single source of truth.** Never edit generated files.
2. After any change to `data/`, run `python scripts/check.py` then `python scripts/build.py`.
3. **Always de-duplicate before adding.** `new_entry.py` checks title, DOI and
   model name/aliases; `check.py` also reports likely duplicates.
4. One model = one file = one primary `category`; any number of `tags`.
5. **Never invent metadata or links.** Leave a field out rather than guess.
6. Set `reviewed: true` only after checking the entry against the paper itself.
7. Write `key` in your own words; never paste abstract sentences.

## Commands

```bash
pip install pyyaml
python scripts/check.py                 # validate; exit 1 on errors
python scripts/build.py                 # regenerate README, data.json, exports
python scripts/new_entry.py model --name X --title "..." --year 2026 \
  --venue bioRxiv --category scrna --tags scrna-seq --paper https://... --code https://github.com/...
python scripts/new_entry.py resource --type benchmark --title "..." --evaluates scgpt,geneformer
```

## Schema

Model file fields: `id` (= file name), `kind: model`, `name`, `aliases`, `title`,
`year` (int), `venue`, `venue_detail`, `category`, `tags`, `modality`,
`architecture`, `task`, `key`, `links`, `model_card`, `citation`, `reviewed`,
`review_notes`.

Resource file fields: `id`, `kind: resource`, `type`, `title`, `aliases`, `year`,
`venue`, `venue_detail`, `tags`, `key`, `links`, `evaluates` (model ids),
`citation`, `reviewed`, `review_notes`.

`links` keys: `paper` (published version if any), `preprint`, `code`, `weights`,
`project`, `dataset`, `docs`, `video`.

`model_card` keys and resource types, categories and tags are defined in
`data/vocab.yaml`; `check.py` rejects anything else. Edit `vocab.yaml` to
add or rename values (its category order = README section order).

## Category ids (models)

`scrna`, `spatial`, `epigenomics`, `multimodal`, `proteomics`, `seq2exp`, `grn`,
`generative`, `morphology`, `llm`, `agents`, `atlas`, `perturbation`, `other`
(fallback only). Labels and descriptions are in `vocab.yaml`. Assign by the
model's PRIMARY purpose, not an incidental task.

Non-models go to resources: benchmarks → `benchmark`; datasets/assays/atlases →
`dataset`; software → `tool`; reviews → `survey`; comments/perspectives/theses →
`perspective`.

## Workflow: "find new papers and add them"

1. **Baseline.** Load `data/models/` + `data/resources/` (titles, names, aliases, DOIs).
2. **Search** for new single-cell FMs and virtual-cell / world models in the
   user's time window (default: anything not already listed). Sources: arXiv
   (q-bio.GN, cs.LG), bioRxiv, Nature Methods/Communications/Cell/Genome Biology,
   NeurIPS/ICLR/ICML, and the reference lists
   (OmicsML/awesome-foundation-model-single-cell-papers — MIT, can import with credit;
   Boom5426/Awesome-Virtual-Cell — no license, use for discovery only, don't copy text).
3. **De-duplicate.** Prefer updating an existing file over adding a preprint-vs-published duplicate.
4. **Extract** name, title, year, venue, modality, architecture, a one-line `key`,
   paper/preprint/code links. Don't invent links.
5. **Categorise** with the ids above; add tags from `vocab.yaml`.
6. **Add** with `new_entry.py` (or write YAML directly for batches).
7. **Check and build**: `python scripts/check.py && python scripts/build.py`.
8. **Report** what you added by category; flag uncertain classifications;
   show the diff before committing.
9. **Commit only after the user confirms.** Message style: `add: <Model> (<year>)`
   or `add: N papers (<categories>)`.

## Open work (see reports/data-quality.md)

- Phase 2: verify every entry against OpenAlex/Crossref/arXiv/bioRxiv (script to run
  in GitHub Actions — this workspace can't reach those APIs), fix venues, add
  preprint → published links, then set `reviewed: true`.
- Entries flagged "possibly not a model" (e.g. Spatial Perturb-seq, CRISPRi Map,
  Perturb-FISH, Comment, Stanford PhD Thesis) — move to resources; several
  already have a duplicate resource entry.
- Auto-derived tags from the migration need human review.
- Phase 3: GitHub Pages site reading `docs/data.json`.
- Phase 4: model cards for flagship models, `evaluates` links on benchmarks,
  weekly paper-finding workflow that opens PRs.
