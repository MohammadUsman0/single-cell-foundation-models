# CSV → YAML migration log

182 models, 121 resources, 19 venues written.

Every entry was migrated with `reviewed: false` and auto-derived tags; verification happens in phase 2.

Changes made during migration:

- tGPT: venue 'Iscience' → 'iScience'
- X-Cell: code link https://vimeo.com/1174241862 stored as project
- Lingshu-Cell: code link https://alibaba-damo-academy.github.io/lingshu-cell-homepage/ stored as project
- spEMO: venue 'Nature Biomedical Eng.' → 'Nature Biomedical Engineering'
- Scouter: venue 'Nature Comp. Science' → 'Nature Computational Science'
- GenePT: venue 'Nature Biomedical Eng.' → 'Nature Biomedical Engineering'
- TEDDY: venue 'ICML Workshop GenBio' → 'ICML' (detail: GenBio Workshop)
- LPM (Large Perturbation Model): venue 'Nature Comp. Science' → 'Nature Computational Science'
- CRISPRi Map: truncated paper link removed (https://www.cell.com/cell-genomics/fulltext/S2666-979X(25)
- scDFM: venue 'ICLR Poster' → 'ICLR' (detail: poster)
- Doloris: venue 'ICLR Poster' → 'ICLR' (detail: poster)
- PETRI: venue 'ICLR Poster' → 'ICLR' (detail: poster)
- CellFlux: venue 'ICML Poster' → 'ICML' (detail: poster)
- PRESCRIBE: venue 'NeurIPS Poster' → 'NeurIPS' (detail: poster)
- OCTO-vc: venue '© by Noetik' is not a venue → blank
- Comment: venue 'Nature Biotechnology Comment' → 'Nature Biotechnology' (detail: Comment)
- Stanford PhD Thesis: venue '© by Yusuf Roohani' is not a venue → blank
- merged duplicate 'OmiCLIP' into 'OmiCLIP / Loki' (same title)
- resource 'Minimal life by computer. Nat Biotechnol (2026). h': type 'Nature Biotech Editorial Paper' → perspective
- resource 'Minimal life by computer. Nat Biotechnol (2026). h': title held a citation; title → 'Minimal life by computer', venue → Nature Biotechnology
- resource 'Towards Virtual Cell Construction by AI': type 'Research statement' → perspective
- Benchmarking Machine Learning Models for Cellular : venue 'NeurIPS Datasets and Benchmarks Track' → 'NeurIPS' (detail: Datasets and Benchmarks Track)
- merged duplicate 'Foundation Models Improve Perturbation Response Prediction' into 'Foundation models improve perturbation response prediction' (same title)
