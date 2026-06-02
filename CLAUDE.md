# CLAUDE.md — instructions for the coding agent

Read this fully before acting. Claude Code reads this file automatically.

## What this project is

An **awesome-list** of single-cell foundation models and AI virtual-cell /
world models, plus the benchmarks, datasets, tools, surveys, perspectives and
venues around them. It is published as a GitHub README, but the README is
**generated**, not hand-written.

Current size: ~178 models, ~118 resources, 19 venues.

## Repository layout

```
.
├── README.md                     # GENERATED — never edit by hand
├── CLAUDE.md                     # this file
├── CONTRIBUTING.md               # human-facing contribution guide
├── LICENSE                       # CC0-1.0
├── data/                         # <-- SOURCE OF TRUTH
│   ├── models.csv
│   ├── resources.csv
│   └── venues.csv
├── scripts/
│   ├── generate_readme.py        # builds README.md from data/*.csv
│   └── add_paper.py              # appends one model row, then regenerates
└── .github/workflows/build-readme.yml
```

## Golden rules

1. **`data/*.csv` is the single source of truth.** All content lives there.
2. **Never edit the tables in `README.md` directly.** Edit the CSV, regenerate.
3. After any change to `data/`, run `python scripts/generate_readme.py`.
4. **Always de-duplicate before adding** (see workflow below).
5. One model = one row = one primary category.
6. **Never invent metadata or links.** Leave a field blank rather than guessing.

## Commands

```bash
python scripts/generate_readme.py        # rebuild README.md from the CSVs
python scripts/add_paper.py --model "X" --title "..." --year 2026 \
  --venue "bioRxiv" --category "<one category below>" \
  --modality "scRNA-seq" --arch "Transformer" --key "one line" \
  --paper "https://..." --code "https://github.com/..."
```

## Data schemas

`models.csv`: `model, title, year, venue, category, modality, arch, task, key, paper, code, citation`
`resources.csv`: `title, year, type, venue, key, paper, links, citation`
  - `type` ∈ {`Evaluation`, `Dataset`, `Tool`, `Perspective`, `Survey`, `Reference`}
`venues.csv`: `name, type, desc, link`

## Model category taxonomy (use the exact string)

Defined in `CATEGORY_ORDER` in `scripts/generate_readme.py`; edit there to
add/rename/reorder. Assign by the model's PRIMARY purpose, not an incidental task.

- `scRNA-seq / Transcriptomics Foundation Models` — general transcriptome FMs.
- `Spatial & Spatial Multi-omics` — spatial transcriptomics / niches / tissue context.
- `Epigenomics & Chromatin Accessibility (scATAC)` — ATAC / chromatin.
- `Multimodal & Multi-omics Integration` — joins modalities.
- `Proteomics & Protein-level Models` — proteomics / spatial proteomics.
- `Sequence-to-Expression & Regulatory Genomics` — DNA→expression.
- `Gene Regulatory Networks & Graph-based Models` — GRN / graph priors.
- `Generative Models (Diffusion / Flow / VAE)` — generative count/expression models.
- `Cell Morphology & Imaging Models` — Cell Painting / morphology / microscopy models.
- `LLM-based & Language-Cell Models` — LLM/text-coupled, or Hyena/Mamba sequence models.
- `Agentic & Autonomous Cell Models` — agents / autonomous experiment & analysis systems.
- `Cross-species & Cell Atlas / Similarity Models` — atlas / cross-species / cell search.
- `Perturbation Prediction & Virtual Cell / World Models` — perturbation response & virtual-cell/world models.
- `Other Single-cell Foundation Models` — fallback only.

## Workflow: "find new papers and add them"

1. **Baseline.** Read `data/models.csv` + `data/resources.csv`; collect existing
   `model` names and `title`s.
2. **Search** for new single-cell FMs and virtual-cell / world models in the
   user's time window (default: anything not already listed). Sources: arXiv
   (q-bio.GN, cs.LG), bioRxiv, Nature Methods/Communications/Cell/Genome Biology,
   NeurIPS/ICLR/ICML, and the reference lists this repo drew from
   (OmicsML/awesome-foundation-model-single-cell-papers,
   Boom5426/Awesome-Virtual-Cell).
3. **De-duplicate** (case-insensitive on name and title). Prefer updating an
   existing row over adding a preprint-vs-published duplicate.
4. **Extract** model, title, year, venue, modality, architecture, a one-line
   `key`, paper URL, code URL. Don't invent links.
5. **Categorise** with the taxonomy above. Benchmarks → resources `Evaluation`;
   datasets → `Dataset`; software → `Tool`; reviews → `Survey`/`Perspective`.
6. **Add** rows (edit CSV directly for batches, or use `add_paper.py`).
7. **Regenerate**: `python scripts/generate_readme.py`.
8. **Report** what you added by category; flag uncertain classifications;
   show the diff before committing.
9. **Commit only after the user confirms.** Message style: `add: <Model> (<year>)`
   or `add: N papers (<categories>)`.

## Known starter tasks (good first jobs)

- Many recently-added rows have blank `modality`, `arch`, and `key`. Fill them in
  from the paper links, a batch at a time, then regenerate.
- A few entries tagged as models are really datasets/assays (e.g. "Spatial
  Perturb-seq", "CRISPRi Map", "Perturb-FISH") — consider moving them to
  `resources.csv` as `Dataset`.
- A few `resources.csv` rows have a wrong `venue` because their title contains
  the word "Cell"; fix opportunistically.

## First-time GitHub setup (if not pushed yet)

```bash
git init && git add -A && git commit -m "initial: single-cell foundation models list"
git branch -M main
git remote add origin https://github.com/<your-username>/single-cell-foundation-models.git
git push -u origin main
```
