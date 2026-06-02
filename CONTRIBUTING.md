# Contributing

This is a **generated** awesome-list. The source of truth is the three CSV
files in [`data/`](data/); `README.md` is built from them. Never edit the
tables in `README.md` by hand — your change would be overwritten on the next
build.

## Add or edit an entry

1. Open the right file:
   - **A model** → [`data/models.csv`](data/models.csv)
   - **A benchmark / survey / perspective** → [`data/resources.csv`](data/resources.csv)
   - **A venue (conference / journal / workshop)** → [`data/venues.csv`](data/venues.csv)
2. Add a row (or edit one). For models, the columns are:

   | column | meaning |
   |---|---|
   | `model` | short model name (e.g. `scGPT`) |
   | `title` | paper title |
   | `year` | publication year |
   | `venue` | journal / preprint server / conference |
   | `category` | one of the headings (see below) |
   | `modality` | data type (scRNA-seq, scATAC, spatial, multi-omics, …) |
   | `arch` | architecture (Transformer, Mamba, diffusion, GNN, …) |
   | `task` | downstream tasks, optional |
   | `key` | one-line description of the contribution |
   | `paper` | URL to paper |
   | `code` | URL to code, optional |
   | `citation` | full citation, optional |

3. Regenerate and open a PR:

   ```bash
   python scripts/generate_readme.py
   git add -A && git commit -m "add <model>" && git push
   ```

   (A GitHub Action also rebuilds `README.md` automatically when `data/`
   changes, so a PR that only touches the CSV is fine.)

### Quick add from the command line

```bash
python scripts/add_paper.py \
  --model "MyModel" --title "MyModel: ..." --year 2026 \
  --venue bioRxiv --category "scRNA-seq / Transcriptomics Foundation Models" \
  --modality "scRNA-seq" --arch "Transformer" \
  --key "What it does in one line." \
  --paper "https://..." --code "https://github.com/..."
```

## Categories

The model categories (and their order in the README) are defined in
`CATEGORY_ORDER` inside [`scripts/generate_readme.py`](scripts/generate_readme.py).
To add, rename, or reorder a category, edit that list. A model may only sit in
one category; pick the closest primary fit.
