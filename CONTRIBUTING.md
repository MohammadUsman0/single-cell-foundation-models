# Contributing

This is a **generated** awesome-list. The source of truth is the YAML files in
[`data/`](data/). `README.md`, `docs/data.json` and `exports/` are built from
them, so never edit those by hand — your change would be overwritten.

Not comfortable with YAML? Just [open an issue](../../issues/new) with the paper
link and we'll add it.

## Layout

```
data/
├── models/<id>.yaml       one file per model
├── resources/<id>.yaml    one file per benchmark, dataset, tool, survey, perspective
├── venues.yaml            conferences, journals and workshops
└── vocab.yaml             allowed categories, resource types, tags and model-card fields
```

## Add an entry

The quickest way is the helper, which also refuses duplicates:

```bash
pip install pyyaml
python scripts/new_entry.py model --name MyModel \
  --title "MyModel: ..." --year 2026 --venue bioRxiv \
  --category scrna --tags scrna-seq,perturbation \
  --paper https://... --code https://github.com/...
python scripts/check.py && python scripts/build.py
```

Or copy an existing file in `data/models/` and edit it. A model file looks like this:

```yaml
id: scgpt                     # must match the file name
kind: model
name: scGPT
title: 'scGPT: toward building a foundation model for single-cell multi-omics using generative AI'
year: 2024
venue: Nature Methods
category: multimodal          # one id from vocab.yaml → decides the README section
tags: [multi-omics, generative]   # any number of ids from vocab.yaml
modality: Single-cell multi-omics # free text
architecture: Transformer         # free text
key: One line, in your own words — not copied from the abstract.
links:
  paper: https://doi.org/10.1038/s41592-024-02201-0
  preprint: https://www.biorxiv.org/content/10.1101/2023.04.30.533534
  code: https://github.com/bowang-lab/scGPT
  weights: https://...
model_card:                   # optional; allowed fields are listed in vocab.yaml
  params: 51M
  pretraining_cells: 33M
  weights: released
  license: MIT
citation: '...'
reviewed: false               # set to true once someone has checked it against the paper
```

Resource files use `type` (`benchmark`, `interpretability`, `dataset`, `tool`, `survey`,
`perspective`, `reference`) instead of `name`/`category`, and a benchmark can
list the models it tested with `evaluates: [scgpt, geneformer]` (only models the paper
actually runs, not ones it cites) and its main result in one line of your own words
with `findings`. An interpretability study (`type: interpretability`) uses the
same `evaluates` and `findings` fields for the models it analyses, plus `interp_method`
(see `interp_methods` in `vocab.yaml`).

Allowed `links` keys: `paper`, `preprint`, `code`, `weights`, `project`,
`dataset`, `docs`, `video`.

## Rules

1. **Never invent metadata or links.** Leave a field out rather than guess.
2. **One model, one file.** If a preprint gets published, update the existing
   file (published link in `paper`, preprint link in `preprint`) — don't add a second one.
3. **Write `key` in your own words.** Don't paste abstract sentences.
4. **`year` is the year the linked version first appeared:** the online-first date
   for a journal article (as in Crossref and OpenAlex), or the first posted version
   for a preprint. Not the journal issue year; `citation` keeps the reference as printed.
5. **Models vs resources:** if it isn't a trained model (a dataset, assay,
   benchmark, review or commentary), it's a resource.
6. Run `python scripts/check.py` before opening a PR. Errors must be fixed;
   warnings are listed in [`reports/data-quality.md`](reports/data-quality.md).

## What a model takes and gives (optional fields)

```yaml
inputs: [expression, perturbation]          # what goes in
outputs: [perturbation-response]            # what comes out
architecture_family: transformer-encoder    # one value; keep details in `architecture`
code_status: none-found                     # only if there is no code link
perturbation_type: [genetic]                # perturbation models only
generalization: [unseen-perturbation]       # perturbation models only
```

Allowed values and their meanings are in [`data/vocab.yaml`](data/vocab.yaml). Set a
value only if the paper, its abstract or the repository states it; leave the field
out otherwise. If nothing fits, propose a new value in your pull request (with a
one-line definition) rather than using the nearest one.

Each entry also records `added` (date, `YYYY-MM-DD`), and may record `sources`
(the URLs its details were checked against) and `review_basis` (`metadata`,
`abstract`, `paper` or `repo`).

## Categories, types and tags

All allowed values live in [`data/vocab.yaml`](data/vocab.yaml). To add or
rename one, edit that file (and any entries that use the old id), then run
`check.py` and `build.py`. The order of categories in `vocab.yaml` is the order
of sections in the README.

A GitHub Action runs `check.py` on every pull request and rebuilds the
generated files when changes reach `main`.
