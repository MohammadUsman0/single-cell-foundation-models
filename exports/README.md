# Exports

Flat copies of the whole catalogue, regenerated from [`data/`](../data/) by `scripts/build.py` on every change.
Don't edit these files by hand: fix the YAML entry in `data/` instead (see [CONTRIBUTING](../CONTRIBUTING.md)).

| File | What it is | Use it for |
|---|---|---|
| `models.csv` | One row per model | Analysis in Excel, R or pandas |
| `resources.csv` | One row per benchmark, interpretability study, dataset, tool, survey or perspective | Same |
| `catalogue.bib` | BibTeX, every entry | LaTeX; import into Zotero, Mendeley or JabRef |
| `catalogue.ris` | RIS, every entry | Import into Zotero, Mendeley or EndNote |

The same data, with everything nested, is in [`docs/data.json`](../docs/data.json), which the website reads.

## CSV conventions

- One row per entry; the `id` column matches the YAML file name in `data/`.
- Fields that hold several values (tags, inputs, outputs, models tested, …) are joined with `; `.
- Empty cell = not recorded. Fields are filled only where the paper or repository states them.
- Allowed values for categories, tags, inputs, outputs, architecture families, perturbation types,
  generalization, interpretability methods and model-card fields are defined in [`data/vocab.yaml`](../data/vocab.yaml).

## Columns

**Both files**

| Column | Meaning |
|---|---|
| `id` | Stable identifier (= YAML file name) |
| `title`, `aliases` | Paper title; other names or earlier titles |
| `year` | Year the linked version first appeared (online-first for journals, first posting for preprints) |
| `venue`, `venue_detail` | Journal, conference or preprint server; extra detail such as a workshop |
| `status` | `published`, `preprint` or `unknown` (derived from the venue) |
| `tags` | Topic tags |
| `key` | One-line summary in our own words |
| `link_paper` … `link_video` | Published version, preprint, code, weights, project page, dataset, docs, video |
| `citation` | Full reference as printed |
| `added` | Date the entry entered the catalogue |
| `review_basis` | What it was checked against: `metadata`, `abstract`, `paper` or `repo` |
| `reviewed` | `True` once checked against the full paper by a maintainer |

**`models.csv` only**

| Column | Meaning |
|---|---|
| `name` | Model name |
| `category` | Primary category (one per model) |
| `modality`, `architecture`, `task` | Free-text descriptions |
| `architecture_family` | Controlled value, e.g. `transformer-encoder`, `diffusion`, `flow-matching`, `agent` |
| `inputs`, `outputs` | What the model takes and gives, e.g. `expression; perturbation` → `perturbation-response` |
| `perturbation_type`, `generalization` | Perturbation models only: `genetic`, `chemical`, … and `unseen-perturbation`, `unseen-cell-context`, … |
| `code_status` | Why there is no code link: `none-found`, `release-pending` or `not-public` |
| `card_*` | Model card: parameters, pretraining cells and data, species, tokenization, objective, context length, weights, licence, package |

**`resources.csv` only**

| Column | Meaning |
|---|---|
| `type` | `benchmark`, `interpretability`, `dataset`, `tool`, `survey`, `perspective` or `reference` |
| `evaluates` | Ids of the catalogued models a benchmark tests or an interpretability study analyses |
| `findings` | The study's main result in one line (our wording) |
| `interp_method` | Interpretability studies: `sparse-autoencoder`, `circuit-tracing`, `attention-analysis`, `probing`, `attribution`, `geometry` |

## BibTeX / RIS notes

Entry keys are the catalogue `id`s. Authors are parsed from each entry's `citation`; long author lists end in
"and others". Where a DOI or arXiv id exists it is included, so a reference manager can refresh the full record.
