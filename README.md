# Awesome Single-Cell Foundation Models & Virtual Cell Modelling [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated, categorised list of foundation models for single-cell biology and AI virtual-cell / world models, plus the benchmarks, perspectives, surveys and venues that surround them.

**178 models · 118 benchmarks/surveys/perspectives · 19 venues** · last generated 2026-06-02.

This list is generated from machine-readable CSVs. **Do not edit the tables below by hand** — edit [`data/models.csv`](data/models.csv), [`data/resources.csv`](data/resources.csv) or [`data/venues.csv`](data/venues.csv) and run `python scripts/generate_readme.py`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Contents

**Models**
- [scRNA-seq / Transcriptomics Foundation Models](#scrna-seq--transcriptomics-foundation-models) (26)
- [Spatial & Spatial Multi-omics](#spatial--spatial-multi-omics) (19)
- [Epigenomics & Chromatin Accessibility (scATAC)](#epigenomics--chromatin-accessibility-scatac) (5)
- [Multimodal & Multi-omics Integration](#multimodal--multi-omics-integration) (5)
- [Proteomics & Protein-level Models](#proteomics--protein-level-models) (4)
- [Sequence-to-Expression & Regulatory Genomics](#sequence-to-expression--regulatory-genomics) (3)
- [Gene Regulatory Networks & Graph-based Models](#gene-regulatory-networks--graph-based-models) (7)
- [Generative Models (Diffusion / Flow / VAE)](#generative-models-diffusion--flow--vae) (2)
- [Cell Morphology & Imaging Models](#cell-morphology--imaging-models) (12)
- [LLM-based & Language-Cell Models](#llm-based--language-cell-models) (21)
- [Agentic & Autonomous Cell Models](#agentic--autonomous-cell-models) (8)
- [Cross-species & Cell Atlas / Similarity Models](#cross-species--cell-atlas--similarity-models) (4)
- [Perturbation Prediction & Virtual Cell / World Models](#perturbation-prediction--virtual-cell--world-models) (61)
- [Other Single-cell Foundation Models](#other-single-cell-foundation-models) (1)

**Resources**
- [Benchmarks & Evaluation](#benchmarks--evaluation)
- [Datasets & Atlases](#datasets--atlases)
- [Tools & Software](#tools--software)
- [Perspectives & Surveys](#perspectives--surveys)
- [Other Resources](#other-resources)
- [Where to Publish & Track New Work](#where-to-publish--track-new-work)

## Models

### scRNA-seq / Transcriptomics Foundation Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **Cell-JEPA** | 2026 | arXiv | Single-cell | FM | - large-scale human kidney scRNA-seq corpus comprising 800,000 cells used | [paper](https://arxiv.org/abs/2602.02093) |
| **CONCORD** | 2026 | Nature Biotechnology | — | — | — | [paper](https://www.nature.com/articles/s41587-025-02950-z) · [code](https://github.com/Gartner-Lab/Concord) |
| **scFM** | 2025 | bioRxiv | Single-cell RNA-seq (Malignant… | scRNA-seq Foundation Model (scF… | present CancerFoundation, a novel single-cell RNA-seq foundation model (scFM) trained exclusively on malignant cells | — |
| **Tabula** | 2025 | Cell | Single-Cell Transcriptomics | Tabular Self-Supervised | Nips 2025 poster | — |
| **scConcept** | 2025 | bioRxiv | Single-cell (technology-agnosti… | transformer-based contrastive l… | present scConcept (“contrastive cell pre-training”), a transformer-based contrastive learning framework that directly optimizes cell embeddings by co… | — |
| **CellFM** | 2025 | Nature Communications | Transcriptomics (100 million hu… | Modified RetNet | Cell annotation, gene function prediction, perturbation response. Key Finding: Uses a modified RetNet for efficiency, 800 million parameters. | — |
| **scPRINT** | 2025 | Nature Communications | Single-cell (50 million cells) | — | Robust gene network predictions | — |
| **Toward a privacy-preserving predictive…** | 2025 | bioRxiv | Single-Cell Transcriptomics | Federated Learning, Tabular Mod… | Privacy-preserving prediction | — |
| **scKGBERT** | 2025 | Genome Biology | — | — | — | — |
| **TEDDY** | 2025 | ICML Workshop GenBio | scRNA-seq | Foundation model family | A family of foundation models for understanding single-cell biology. | [paper](https://arxiv.org/pdf/2503.03485) |
| **scPEFT** | 2025 | Nature Machine Intell… | scRNA-seq | Parameter-efficient fine-tuning | Parameter-efficient fine-tuning for single-cell LLMs. | [paper](https://www.nature.com/articles/s42256-025-01170-z) |
| **SubCell** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2024.12.06.627299) · [code](https://github.com/CellProfiling/subcell-embed) |
| **ProteinTalks** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.02.07.637070) · [code](https://github.com/guomics-lab/PTV-1/tree/main/ProteinTalks) |
| **AIDO.Cell Scaling Dense Representations** | 2024 | bioRxiv | Single Cell Transcriptome | — | Develop AIDO.Cell, a pretrained module for representing gene expression and cellular systems in an AI-driven Digital Organism | — |
| **scLong** | 2024 | bioRxiv | Single-Cell Transcriptomics | Billion-Parameter | Capturing long-range gene context | — |
| **scFoundation** | 2024 | Nature | Single-cell Transcriptomics | Asymmetric Transformer-like | Gene expression enhancement, drug response prediction, cell type annotation. Key Finding: Achieves SOTA performance in diverse tasks. | — |
| **Learning multi-cellular representations…** | 2024 | Nature | Single-Cell Transcriptomics | — | Characterization of patient-level disease states | — |
| **scNET** | 2024 | Nature Methods | Single-cell Gene Expression + P… | — | Learning context-specific gene/cell embeddings | — |
| **xTrimoGene** | 2024 | NeurIPS | Single-Cell RNA-Seq | — | Efficient and Scalable Representation Learner | [code](https://github.com/biomap-research/scFoundation) |
| **scTab** | 2024 | Nature Communications | — | — | — | [paper](https://doi.org/10.1038/s41467-024-51059-5) · [code](https://github.com/theislab/scTab) |
| **single-cell masked autoencoder (scMAE)** | 2023 | NeurIPS | - | Masked Autoencoder | Automated Immunophenotyper | — |
| **scCLIP** | 2023 | NeurIPS | Multi-modal Single-cell | Contrastive Learning | Integration Pre-training | [code](https://github.com/jsxlei/scCLIP) |
| **CellLM Large-Scale Cell Representation…** | 2023 | arXiv | - | Divide-and-Conquer Contrastive… | propose a novel divide-and-conquer contrastive learning approach to decouple the batch size from the GPU memory size for cell representation learning | [paper](https://arxiv.org/abs/2306.04371) |
| **tGPT** | 2023 | Iscience | Large-scale Transcriptomes (22.… | Generative Pretraining (Autoreg… | tGPT models gene rankings via autoregressive language modeling tGPT works effectively on fundamental single-cell analysis tasks tGPT captures distinc… | — |
| **scPretrain** | 2022 | Bioinformatics | - | Multi-task Self-Supervised Lear… | Cell-type classification | — |
| **ProCyon** |  | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2024.12.10.627665) · [code](https://github.com/mims-harvard/ProCyon) |

### Spatial & Spatial Multi-omics

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **Spatial Perturb-seq** | 2026 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-026-69677-6) · [code](https://github.com/kimberle9/spatialperturbseq) |
| **Celcomen** | 2026 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-026-69856-5) · [code](https://github.com/Teichlab/celcomen) |
| **stVCR** | 2026 | Nature Methods | — | — | — | [paper](https://www.nature.com/articles/s41592-026-03010-3) · [code](https://github.com/QiangweiPeng/stVCR) |
| **SpaTranslator** | 2025 | bioRxiv | Spatial Multi-omics | deep generative model | present SpaTranslator, a deep generative framework that integrates graph neural networks with an adversarial variational generative model to fully ca… | — |
| **Nicheformer** | 2025 | Nature | Single-cell and Spatial Omics | — | - | — |
| **SWITCH** | 2025 | Nature Computational… | Spatial Multi-omics | generative model | Introduce SWITCH (Spatially Weighted Multi-omics Integration and Cross-modal Translation with Cycle-mapping Harmonization), a deep generative model f… | — |
| **stFormer A framework for gene represent…** | 2025 | bioRxiv | Spatial Transcriptomics | Transformer (Self-Attention, Cr… | propose a biased cross-attention method that enables the model to do learning with single-cell resolution on whole-transcriptome but low-resolution V… | — |
| **SToFM** | 2025 | arXiv | Spatial Transcriptomics | — | Multi-scale modeling | [paper](https://arxiv.org/abs/2507.11588) |
| **OmiCLIP / Loki** | 2025 | Nature Methods | Histopathology Image + Spatial… | Visual-Omics (Contrastive Learn… | Cell-type decomposition, ST gene expression prediction, image–transcriptomics retrieval. Key Finding: Bridges visual and molecular data by converting… | — |
| **scGPT-spatial** | 2025 | bioRxiv | Spatial Transcriptomics | Continual Pretraining | scGPT-spatial introduces a novel MoE (Mixture of Experts) decoder that adaptively routes samples for protocol-aware decoding of gene expression profi… | — |
| **OmniCell** | 2025 | bioRxiv | scRNA-seq + spatial | Unified FM | Unified FM over single-cell and spatial transcriptomics. | [paper](https://www.biorxiv.org/content/10.64898/2025.12.29.696804v1) |
| **STPath** | 2025 | npj Digital Medicine | Spatial transcriptomics + WSI | Generative FM | Generative FM integrating spatial transcriptomics and whole-slide images. | [paper](https://www.nature.com/articles/s41746-025-02020-3) |
| **Perturb-FISH** | 2025 | Cell | — | — | — | [paper](https://doi.org/10.1016/j.cell.2025.02.012) |
| **GraphVelo** | 2025 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-025-62784-w) · [code](https://github.com/xing-lab-pitt/GraphVelo) |
| **Stereo-Cell** | 2025 | Science | — | — | — | [paper](https://doi.org/10.1126/science.adr0475) · [code](https://github.com/haoshijie13/Stereo-cell-paper-code) |
| **NicheFlow** | 2025 | NeurIPS | — | — | — | [paper](https://openreview.net/forum?id=5ofJyjgrth) · [code](https://github.com/kristiyansakalyan/nicheflow) |
| **OmiCLIP** | 2025 | Nature Methods | — | — | — | [paper](https://doi.org/10.1038/s41592-025-02707-1) · [code](https://github.com/GuangyuWangLab2021/Loki) |
| **Novae** | 2024 | bioRxiv | Spatial Transcriptomics | Graph-based | - | [code](https://github.com/MICS-Lab/novae) |
| **nichecompass** | 2024 | bioRxiv | - | Knowledge-Informed Cross-Specie… | Deciphering universal gene regulatory mechanisms | [code](https://github.com/Lotfollahi-lab/nichecompass) |

### Epigenomics & Chromatin Accessibility (scATAC)

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **Atacformer** | 2025 | bioRxiv | scATAC-seq | Transformer-based | Clustering, cell-type annotation, batch correction, RNA imputation (via CRAFT model). Key Finding: Generates embeddings for individual cis-regulatory… | — |
| **ChromFound** | 2025 | arXiv | scATAC-seq (Chromatin Accessibi… | Hybrid (Mamba + Self-Attention) | Cell representation, cell type annotation, cross-omics prediction, identifies gene-enhancer relationships. Key Finding: Hybrid architecture to handle… | [paper](https://arxiv.org/abs/2505.12638) |
| **EpiFoundation** | 2025 | bioRxiv | scATAC-seq | — | Cell-type annotation, batch correction, gene expression prediction. Key Finding: Uses cross-modality pre-training (peak-to-gene alignment) on non-zer… | — |
| **EpiAgent** | 2025 | Nature Methods | scATAC-seq (Single-cell Epigeno… | Transformer-based (Bidirectiona… | Unsupervised feature extraction, supervised cell type annotation, data imputation, cellular response prediction (perturbations). Key Finding: Encodes… | — |
| **SCARF** | 2025 | bioRxiv | Single Cell ATAC-seq and RNA-seq | — | - | — |

### Multimodal & Multi-omics Integration

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **spEMO** | 2026 | Nature Biomedical Eng. | Spatial multi-omics + histopath… | Multimodal FM | Multi-modal FM for spatial multi-omic and histopathology data. | [paper](https://www.biorxiv.org/content/10.1101/2025.01.13.632818v3) |
| **PETRI** | 2026 | ICLR Poster | — | — | — | [paper](https://openreview.net/forum?id=Vu8YXDooG5) |
| **scLinguist** | 2025 | bioRxiv | Single-cell Multi-omics | Hyena-based | Cross-modality translation | — |
| **CAPTAIN** | 2025 | bioRxiv | Single-cell RNA and Protein (co… | Multimodal | Protein imputation, cell type annotation, batch harmonization. Key Finding: Learns unified multimodal representations; uncovers protein-driven interc… | — |
| **scGPT** | 2024 | Nature | Single-cell Multi-omics | Generative Pre-trained Transfor… | Single-cell multi-omics, capturing biological insights into genes and cells. | — |

### Proteomics & Protein-level Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **scTranslator** | 2025 | Nature Biomedical Eng… | Single-cell Transcriptome | Large Generative Model | Translating transcriptome to proteome (protein imputation). Key Finding: Confirmed accuracy across various profiling techniques (CITE-seq, REAP-seq,… | — |
| **Spatial Proteomics FM** | 2025 | arXiv | Spatial proteomics | Foundation model | A foundation model for spatial proteomics. | [paper](https://arxiv.org/abs/2506.03373) |
| **scPROTEIN** | 2024 | Nature Methods | Single-cell Proteomics | Deep Graph Contrastive Learning | Single-cell proteomics embedding | — |
| **scmFormer** | 2024 | Advanced Science | Single-Cell Proteomics and Tran… | Multi-Task Transformer | Integrates large-scale data | — |

### Sequence-to-Expression & Regulatory Genomics

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **GET (General Expression Transformer)** | 2025 | Nature | Chromatin Accessibility, Sequen… | Transformer | Predicting gene expression in seen/unseen cell types, regulatory inference. Key Finding: Achieves experimental-level accuracy; learns regulatory gram… | — |
| **Borzoi Predicting RNA-seq coverage** | 2025 | Nature Genetics | RNA-seq Coverage from DNA Seque… | — | a model that learns to predict cell-type-specific and tissue-specific RNA-seq coverage from DNA sequence. Using statistics derived from Borzoi’s pred… | [code](https://github.com/calico/borzoi) |
| **Single-cell gene expression prediction** | 2023 | bioRxiv | Single-cell Gene Expression fro… | — | Here, we use a transfer learning framework, seq2cells, leveraging a pre-trained epigenome model for gene expression prediction from large sequence co… | — |

### Gene Regulatory Networks & Graph-based Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **GREmLN** | 2026 | Cell | Single-cell | FM | Issue: standard language models such as transformers benefits from sequentially structured data with well defined absolute or relative positional rel… | — |
| **CellProphet** | 2025 | bioRxiv | — | Transformer-based | present CellProphet, an interpretable AI model that infers dynamic GRN by integrating temporal causality with transformer self-attention mechanism | [code](https://github.com/prsigma/CellProphet) |
| **Cell-GraphCompass** | 2025 | National Science Revi… | Single-cell Transcriptomics | Graph Pre-training | Batch integration, cell type annotation, gene perturbation, in silico gene knockout. Key Finding: Pioneer in using graph pre-training to model genes… | — |
| **scCello** | 2024 | Cell | Transcriptome | — | - | — |
| **GeneCompass** | 2024 | Cell Research | — | — | — | — |
| **MuSe-GNN** | 2023 | — | Multimodal Biological Graph Data | GNN | Learning unified gene representation | — |
| **GeneFormer** | 2023 | Nature | Single-Cell Transcriptomics | Transformer (Ordinal Positions) | Predictions in network biology. Key Finding: Uses ordinal positions of tokenized genes, trained on 30 million cells. | — |

### Generative Models (Diffusion / Flow / VAE)

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **scLDM** | 2025 | arXiv | Single-Cell Gene Expression | Diffusion Model | introduce a scalable latent diffusion model (scLDM) for single-cell gene expression data. authors shows superior performance in a variety of experime… | [paper](https://arxiv.org/abs/2511.02986) |
| **Diffusion debiasing (perturbation)** | 2025 | PNAS | scRNA-seq (perturbation) | Diffusion | Diffusion-based debiasing for single-cell transcriptional response prediction. | [paper](https://www.pnas.org/doi/10.1073/pnas.2525268122) |

### Cell Morphology & Imaging Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **IMPA** | 2025 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-024-55707-8) · [code](https://github.com/theislab/IMPA) |
| **PhenoProfiler** | 2025 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-025-60033-1) · [code](https://github.com/QSong-github/PhenoProfiler) |
| **PERISCOPE** | 2025 | Nature Methods | — | — | — | [paper](https://www.nature.com/articles/s41592-024-02537-7) · [code](https://github.com/broadinstitute/2022_PERISCOPE) |
| **Morph Map** | 2025 | Nature Methods | — | — | — | [paper](https://www.nature.com/articles/s41592-025-02753-9) · [code](https://github.com/jump-cellpainting/2025_Chandrasekaran_NatureMethods_Morphmap) |
| **MorphDiff** | 2025 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-025-63478-z) · [code](https://github.com/biomap-research/MorphDiff) |
| **CellFlux** | 2025 | ICML Poster | — | — | — | [paper](https://openreview.net/forum?id=3NLNmdheIi) · [code](https://github.com/yuhui-zh15/CellFlux) |
| **CellCLIP** | 2025 | NeurIPS | — | — | — | [paper](https://papers.nips.cc/paper_files/paper/2025/hash/b4689a8e6ac04c0919f7162365f1248d-Abstract-Conference.html) · [code](https://github.com/suinleelab/CellCLIP) |
| **CELTIC** | 2025 | Nature Methods | — | — | — | [paper](https://www.nature.com/articles/s41592-025-02960-4) · [code](https://github.com/zaritskylab/CELTIC) |
| **MorphoDiff** | 2025 | ICLR | — | — | — | [paper](https://openreview.net/forum?id=PstM8YfhvI) · [code](https://github.com/bowang-lab/MorphoDiff) |
| **CLIP^n** | 2025 | Nature Biotechnology | — | — | — | [paper](https://doi.org/10.1038/s41587-025-02729-2) · [code](https://github.com/AltschulerWu-Lab/CLIPn) |
| **CellFlow** | 2025 | bioRxiv | — | — | — | [paper](https://www.biorxiv.org/content/10.1101/2025.04.11.648220v1.full.pdf) · [code](https://github.com/theislab/CellFlow) |
| **Cell Shapes** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.05.13.653868) |

### LLM-based & Language-Cell Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **OKR-Cell** | 2026 | bioRxiv | scRNA-seq + text | Cross-modal pre-training | Open-world-knowledge-aided cell-language foundation model. | [paper](https://www.biorxiv.org/content/10.64898/2026.01.09.698573v1) |
| **scELMo** | 2025 | bioRxiv | Single-cell Data | Language Models | propose a method named scELMo (Single-cell Embedding from Language Models), to analyze single-cell data that utilizes Large Language Models (LLMs) as… | — |
| **CASSIA** | 2025 | Nature Communications | scRNA-seq | Multi-agent LLM | Multi-agent LLM for automated, interpretable cell-type annotation. | [paper](https://www.nature.com/articles/s41467-025-67084-x) |
| **TissueNarrator** | 2025 | bioRxiv | Spatial transcriptomics | Generative LLM | Generative modeling of spatial transcriptomics with LLMs. | [paper](https://www.biorxiv.org/content/10.1101/2025.11.24.690325v1) |
| **CellHermes** | 2025 | bioRxiv | Multi-omics + text | LLM | Harmonizes multimodal omics data via language for omics understanding. | [paper](https://www.biorxiv.org/content/10.1101/2025.11.07.687322v1) |
| **CellTok** | 2025 | bioRxiv | scRNA-seq | Early-fusion multimodal LLM | Early-fusion multimodal LLM for single-cell transcriptomics via tokenization. | [paper](https://www.biorxiv.org/content/10.1101/2025.10.22.684047v1) |
| **sciLaMA** | 2025 | ICML | scRNA-seq | LLM-prior representation learni… | Leverages LLM prior knowledge for single-cell representation learning. | [paper](https://openreview.net/forum?id=0m4VsLwj5s) |
| **C2S-Scale** | 2025 | bioRxiv | scRNA-seq | LLM (cell sentences) | Scales LLMs over 'cell sentences' for next-generation single-cell analysis. | [paper](https://www.biorxiv.org/content/10.1101/2025.04.14.648850v1) |
| **GenePT** | 2025 | Nature Biomedical Eng. | scRNA-seq | LLM text embeddings | Builds single-cell embeddings from ChatGPT gene/text descriptions. | [paper](https://www.nature.com/articles/s41551-024-01284-6) |
| **scMamba (Bidirectional Mamba)** | 2025 | arXiv | scRNA-seq | Bidirectional Mamba | Efficient long-context single-cell modeling with bidirectional Mamba. | [paper](https://arxiv.org/abs/2504.16956) |
| **scMulan** | 2024 | Nature | Single-cell | Multitask Generative Pre-traine… | Single-cell analysis | — |
| **LangCell** | 2024 | arXiv | - | Language-Cell Pre-training | introduce , the first uage- pre-training framework. LangCell utilizes texts enriched with cell identity information to gain a profound comprehension… | [paper](https://arxiv.org/abs/2405.06708) |
| **SATURN** | 2024 | Nature Methods | Single-cell RNA-seq | Deep Learning (Protein Language… | Integrating datasets across species, universal cell embeddings. Key Finding: Encodes genes' biological properties using protein language models to tr… | — |
| **CELLama** | 2024 | bioRxiv | scRNA-seq + spatial | Language-model embedding | Cell embeddings for sc + spatial transcriptomics via LLM abilities. | [paper](https://www.biorxiv.org/content/10.1101/2024.05.08.593094v1) |
| **scChat** | 2024 | bioRxiv | scRNA-seq | LLM copilot | LLM-powered copilot for contextualized scRNA-seq analysis. | [paper](https://www.biorxiv.org/content/10.1101/2024.10.01.616063v1) |
| **Cell2Sentence** | 2024 | ICML | scRNA-seq | LLM (cell sentences) | Represents cells as text sentences to teach LLMs the language of biology. | [paper](https://www.biorxiv.org/content/10.1101/2023.09.11.557287v1) |
| **scReader** | 2024 | arXiv | scRNA-seq | LLM prompting | Prompts LLMs to interpret scRNA-seq data. | [paper](https://arxiv.org/abs/2412.18156) |
| **CellPLM** | 2023 | bioRxiv | Single-cell (Cells as tokens, t… | Pre-trained Transformer | Diverse downstream tasks. Key Finding: First sc-pre-trained transformer to encode cell-cell relations; 100x faster inference. | — |
| **scHyena** | 2023 | arXiv | Full-Length Single-Cell RNA-Seq | Hyena-based | Analysis in Brain | [paper](https://arxiv.org/abs/2310.02713) |
| **Exceiver** | 2022 | arXiv | Single-cell Gene Expression | Language Model | Single-cell gene expression language model | [paper](https://arxiv.org/abs/2210.14330) |
| **scBERT** | 2022 | Nature Machine Intell… | Single-cell RNA-seq | Deep Language Model | Cell type annotation. Key Finding: Uses value categorization (binning) for gene counts, transforming continuous data to categorical values. | — |

### Agentic & Autonomous Cell Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **CRISPR-GPT** | 2025 | Nature Biomedical Eng… | — | — | — | [paper](https://doi.org/10.1038/s41551-025-01463-z) · [code](https://github.com/cong-lab/crispr-gpt-pub) |
| **Cell-o1** | 2025 | arXiv | — | — | — | [paper](https://arxiv.org/abs/2506.02911) · [code](https://github.com/ncbi-nlp/cell-o1) |
| **rBio-1** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.08.18.670981) · [code](https://github.com/czi-ai/rbio) |
| **CellAtria** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.07.31.667880) · [code](https://github.com/AstraZeneca/cellatria) |
| **SpatialAgent** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.04.03.646459) · [code](https://github.com/Genentech/SpatialAgent) |
| **GeneAgent** | 2025 | Nature Methods | — | — | — | [paper](https://doi.org/10.1038/s41592-025-02748-6) · [code](https://github.com/ncbi-nlp/GeneAgent) |
| **CellVoyager** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.06.03.657517) · [code](https://github.com/zou-group/CellVoyager) |
| **Biomni** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.05.30.656746) · [code](https://github.com/snap-stanford/biomni) |

### Cross-species & Cell Atlas / Similarity Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **SCimilarity** | 2025 | Nature | Single-Cell Transcriptomics | Metric-Learning Framework | Scalable search of similar human cells, rapid queries of millions of profiles. | — |
| **TranscriptFormer** | 2025 | bioRxiv | Single-Cell (Transcriptome) | Transformer | Cross-species generative cell atlas (1.5 Billion Years of Evolution) predict cell type-specific transcription factors and gene-gene interactions that… | — |
| **UCE** | 2024 | bioRxiv | — | — | — | [paper](https://www.biorxiv.org/content/10.1101/2023.11.28.568918v2) · [code](https://github.com/snap-stanford/UCE) |
| **scPoli** | 2023 | Nature Methods | Single-cell datasets | — | Population-level integration, multi-scale analysis | — |

### Perturbation Prediction & Virtual Cell / World Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **STACK** | 2026 | bioRxiv | — | — | — | — |
| **PerturbGen** | 2026 | bioRxiv | Single-cell | Transformer | cell state transition prediction, gene program dicovery, in silico perturbations | [code](https://github.com/Lotfollahi-lab/Perturbgen/) |
| **X-Cell** | 2026 | bioRxiv | Single-cell | — | — | [code](https://vimeo.com/1174241862) |
| **Lingshu-Cell** | 2026 | arXiv | Single-cell | masked discrete diffusion model | masked discrete diffusion model that learns transcriptomic state distributions and supports conditional simulation under perturbation | [paper](https://arxiv.org/abs/2603.25240) · [code](https://alibaba-damo-academy.github.io/lingshu-cell-homepage/) |
| **AlphaCell** | 2026 | bioRxiv | — | — | — | — |
| **SCALE** | 2026 | bioRxiv | — | — | — | — |
| **AetherCell** | 2026 | bioRxiv | — | — | — | — |
| **Discrete Cell Models (DCM)** | 2026 | bioRxiv | — | — | results establish discrete diffusion as a promising direction for foundational models of cellular biology | — |
| **ProtiCelli** | 2026 | bioRxiv | — | — | — | [paper](https://doi.org/10.64898/2026.03.31.715748) · [code](https://github.com/CellProfiling/ProtiCelli) |
| **CRISPRi Map** | 2026 | Cell Genomics | — | — | — | [paper](https://www.cell.com/cell-genomics/fulltext/S2666-979X(25) |
| **TxPert** | 2026 | Nature Biotechnology | — | — | — | [paper](https://www.nature.com/articles/s41587-026-03113-4) · [code](https://github.com/valence-labs/TxPert) |
| **scDFM** | 2026 | ICLR Poster | — | — | — | [paper](https://openreview.net/forum?id=QSGanMEcUV) · [code](https://github.com/AI4Science-WestlakeU/scDFM) |
| **Doloris** | 2026 | ICLR Poster | — | — | — | [paper](https://openreview.net/forum?id=rvpDHfoTd2) · [code](https://github.com/ChangxiChi/Doloris) |
| **Departures** | 2026 | AAAI | — | — | — | [paper](https://ojs.aaai.org/index.php/AAAI/article/view/39190) |
| **STRAND** | 2026 | arXiv | — | — | — | [paper](https://arxiv.org/abs/2602.10156) |
| **PerturbDiff** | 2026 | arXiv | — | — | — | [paper](https://arxiv.org/abs/2602.19685) |
| **scBIG** | 2026 | arXiv | — | — | — | [paper](https://arxiv.org/abs/2602.04901) |
| **CellxPert** | 2026 | arXiv | — | — | — | [paper](https://arxiv.org/abs/2605.00930) |
| **VCWorld** | 2025 | arXiv | — | LLM based | present VCWorld, a cell-level white-box simulator that integrates structured biological knowledge with the iterative reasoning capabilities of large… | [paper](https://arxiv.org/abs/2512.00306) · [code](https://github.com/GENTEL-lab/VCWorld) |
| **PULSAR** | 2025 | bioRxiv | Multi-scale and Multicellular B… | unknown | - | — |
| **CellTRIP** | 2025 | bioRxiv | — | reinforcement learning | CellTRIP, Inferring virtual cell environments using multi-agent reinforcement learning for spatiotemporal trajectory interpolation, imputation, and p… | [code](https://github.com/daifengwanglab/CellTRIP) |
| **Tahoe-x1** | 2025 | bioRxiv | Single-Cell (Perturbation-Train… | — | Tx1 jointly learns representations of genes, cells, and compounds using a masked-expression generative objective that incorporates a drug token, enab… | — |
| **Multimodal foundation model** | 2025 | bioRxiv | Multimodal (not specified) | — | Predicts zero-shot functional perturbations and cell fate dynamics | — |
| **CellForge** | 2025 | arXiv | — | Agentic | — | [paper](https://arxiv.org/abs/2508.02276) · [code](https://github.com/gersteinlab/CellForge) |
| **STATE** | 2025 | bioRxiv | — | — | — | — |
| **Scouter** | 2025 | Nature Comp. Science | scRNA-seq + LLM embeddings | LLM-embedding model | Predicts transcriptional responses to genetic perturbations using LLM embeddings. | [paper](https://www.nature.com/articles/s43588-025-00912-8) |
| **GeneJEPA** | 2025 | bioRxiv | scRNA-seq | JEPA world model | A predictive (JEPA) world model of the transcriptome. | [paper](https://www.biorxiv.org/content/10.1101/2025.10.14.682378v1) |
| **SpatialProp** | 2025 | bioRxiv | Spatial transcriptomics | Perturbation model | Tissue perturbation modeling with spatially resolved single-cell data. | [paper](https://www.biorxiv.org/content/10.64898/2025.11.30.691355v1) |
| **PertAdapt** | 2025 | bioRxiv | scRNA-seq (perturbation) | Adapter on scFMs | Condition-sensitive adaptation of scFMs for genetic perturbation prediction. | [paper](https://www.biorxiv.org/content/10.1101/2025.11.21.689655v1) |
| **LPM (Large Perturbation Model)** | 2025 | Nature Comp. Science | scRNA-seq (perturbation) | Large perturbation model | Large perturbation models for in-silico biological discovery. | [paper](https://www.nature.com/articles/s43588-025-00870-1) |
| **GPerturb** | 2025 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-025-61165-7) · [code](https://github.com/hwxing3259/GPerturb) |
| **CellNavi** | 2025 | Nature Cell Biology | — | — | — | [paper](https://doi.org/10.1038/s41556-025-01755-1) · [code](https://github.com/DLS5-Omics/CellNavi) |
| **PRESCRIBE** | 2025 | NeurIPS Poster | — | — | — | [paper](https://openreview.net/forum?id=A5O41ntKjk) |
| **Cradle-VAE** | 2025 | AAAI | — | — | — | [paper](https://ojs.aaai.org/index.php/AAAI/article/view/33695) · [code](https://github.com/dmis-lab/CRADLE-VAE) |
| **XTransferCDR** | 2025 | AAAI | — | — | — | [paper](https://ojs.aaai.org/index.php/AAAI/article/view/34073) · [code](https://github.com/hliulab/XTransferCDR) |
| **Theory** | 2025 | Cell | — | — | — | [paper](https://doi.org/10.1016/j.cell.2025.06.048) · [code](https://github.com/physicell-models/grammar_samples) |
| **CausCell** | 2025 | Nature Communications | — | — | — | [paper](https://doi.org/10.1038/s41467-025-62008-1) · [code](https://github.com/bm2-lab/CausCell) |
| **DrugPT** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.07.25.665130) |
| **OmniPert** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.07.02.662744) |
| **UNAGI** | 2025 | Nature Biomedical Eng… | — | — | — | [paper](https://doi.org/10.1038/s41551-025-01423-7) · [code](https://github.com/mcgilldinglab/UNAGI) |
| **OCTO-vc** | 2025 | © by Noetik | — | — | — | — |
| **UniPert-G2CP** | 2025 | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2025.02.02.635055) · [code](https://github.com/TencentAILabHealthcare/UniPert) |
| **UniCure** | 2025 | bioRxiv | — | — | — | [paper](https://www.biorxiv.org/content/10.1101/2025.06.14.658531v1) · [code](https://github.com/ZexiChen502/UniCure) |
| **Comment** | 2025 | Nature Biotechnology… | — | — | — | [paper](https://www.nature.com/articles/s41587-025-02583-2) |
| **Cell Maps** | 2025 | Nature | — | — | — | [paper](https://doi.org/10.1038/s41586-025-08878-3) |
| **Prophet** | 2025 | bioRxiv | — | — | — | [paper](https://www.biorxiv.org/content/10.1101/2024.08.12.607533v2.full.pdf) · [code](https://github.com/theislab/prophet) |
| **PS** | 2025 | Nature Cell Biology | — | — | — | [paper](https://doi.org/10.1038/s41556-025-01626-9) · [code](https://github.com/davidliwei/PS) |
| **Mixscale** | 2025 | Nature Cell Biology | — | — | — | [paper](https://doi.org/10.1038/s41556-025-01622-z) · [code](https://github.com/satijalab/Mixscale) |
| **scLAMBDA** | 2024 | bioRxiv | scRNA-seq (perturbation) | Generative model | Predicts single-cell multi-gene perturbation responses. | [paper](https://www.biorxiv.org/content/10.1101/2024.12.04.626878v1) |
| **scGenePT** | 2024 | bioRxiv | scRNA-seq (perturbation) | Language-augmented | Language-augmented modeling of single-cell perturbations. | [paper](https://www.biorxiv.org/content/10.1101/2024.10.23.619972v1) |
| **TranSiGen** | 2024 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-024-49620-3) · [code](https://github.com/myzhengSIMM/TranSiGen) |
| **PRnet** | 2024 | Nature Communications | — | — | — | [paper](https://www.nature.com/articles/s41467-024-53457-1) |
| **Stanford PhD Thesis** | 2024 | © by Yusuf Roohani | — | — | — | [paper](https://stacks.stanford.edu/file/jw766pz3938/PhD_Thesis_Roohani_Yusuf_2024-augmented.pdf) |
| **CellPolaris** | 2023 | bioRxiv | Transcriptomic Data | Transfer Learning | Generating cell-type-specific Gene Regulatory Networks (GRNs), simulating in-silico perturbations. Key Finding: Relies exclusively on transcriptomic… | — |
| **CINEMA-OT** | 2023 | Nature Methods | scRNA-seq (perturbation) | Optimal transport (causal) | Causal identification of single-cell perturbation effects via optimal transport. | [paper](https://www.nature.com/articles/s41592-023-02040-5) |
| **TwinCell** |  | bioRxiv | Single-cell | — | identifies the upstream regulators most likely to drive the transition between two cell states, such as diseased and healthy, by decomposing target p… | — |
| **X-Pert** |  | bioRxiv | — | — | — | [paper](https://www.biorxiv.org/content/10.1101/2025.11.13.688367v2) · [code](https://github.com/Chen-Li-17/X-Pert) |
| **HarmonyCell** |  | bioRxiv | — | — | — | [paper](https://arxiv.org/pdf/2603.01396) |
| **Squidiff** |  | Nature Methods | — | — | — | [paper](https://www.nature.com/articles/s41592-025-02877-y) · [code](https://github.com/siyuh/Squidiff) |
| **ADLF** |  | Science | — | — | — | [paper](https://doi.org/10.1126/science.adi8577) · [code](https://doi.org/10.5281/zenodo.16921928) |
| **RegVelo** |  | bioRxiv | — | — | — | [paper](https://doi.org/10.1101/2024.12.11.627935) · [code](https://github.com/theislab/regvelo) |

### Other Single-cell Foundation Models

| Model | Year | Venue | Modality | Architecture | Key idea | Links |
|---|---|---|---|---|---|---|
| **scPRINT-2** | 2026 | bioRxiv | — | — | propose an additive benchmark across a gymnasium of tasks to discover which features improve performance. From thesefindings, we present scPRINT-2, a… | — |

## Benchmarks & Evaluation

| Title | Year | Venue | Notes | Links |
|---|---|---|---|---|
| AssayBench: An Assay-Level Virtual Cell Benchmark for LLMs and Agents | 2026 | arXiv | — | [link](https://arxiv.org/abs/2605.10876) |
| Towards Autonomous Mechanistic Reasoning in Virtual Cells | 2026 | arXiv | — | [link](https://arxiv.org/abs/2604.11661) |
| A Systematic Comparison of Single-Cell Perturbation Response Prediction Models | 2026 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2024.12.23.630036v2) |
| A unified framework enables accessible deployment and comprehensive benchmarking of singl… | 2026 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.64898/2026.01.06.698060v1) |
| Perturbench: Benchmarking machine learning models for cellular perturbation analysis | 2025 | arXiv | PerturBench a comprehensive framework for modeling single cell transcriptomic responses to perturbations, aimed at standardizing benchmarking | [link](https://arxiv.org/abs/2408.10609) |
| What do single-cell models already know about perturbations? | 2025 | — | We train variational autoencoders on three gene expression datasets spanning genetic, chemical, and temporal perturbations, and infer perturbations b… | [link](https://github.com/yhsure/perturbations) |
| Effects of Distance Metrics and Scaling on the Perturbation Discrimination Score | 2025 | arXiv | Perturbation Discrimination Score (PDS) is increasingly used to evaluate whether predicted perturbation effects remain distinguishable, including in… | [link](https://arxiv.org/abs/2511.16954) |
| Virtual Cell Challenge: Toward a Turing test for the virtual cell | 2025 | Cell | — | — |
| Defining and benchmarking open problems in single-cell analysis | 2025 | Nature Biotechnology | — | [link](https://www.nature.com/articles/s41587-025-02694-w) |
| Benchmarking algorithms for generalizable single-cell perturbation response prediction | 2025 | Nature Methods | — | [link](https://www.nature.com/articles/s41592-025-02980-0) |
| scCluBench: Comprehensive Benchmarking of Clustering Algorithms for Single-Cell RNA Seque… | 2025 | arXiv | — | [link](https://arxiv.org/abs/2512.02471) |
| HEIMDALL: A Modular Framework for Tokenization in Single-Cell Foundation Models | 2025 | bioRxiv | Modular tokenization framework for scFMs. | [link](https://www.biorxiv.org/content/10.1101/2025.11.09.687403v2) |
| Empirical Evaluation of Single-Cell Foundation Models for Predicting Cancer Outcomes | 2025 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2025.10.31.685892v1) |
| Benchmarking cell type and gene set annotation by large language models with AnnDictionary | 2025 | Nature Communicatio… | — | [link](https://www.nature.com/articles/s41467-025-64511-x) |
| Sparse Autoencoders Reveal Interpretable Features in Single-Cell Foundation Models | 2025 | bioRxiv | Interpretability via sparse autoencoders. | [link](https://www.biorxiv.org/content/10.1101/2025.10.22.681631v1) |
| Reusability report: transferability of self-supervised learning models from single-cell t… | 2025 | Nature Machine Inte… | — | [link](https://www.nature.com/articles/s42256-025-01097-5) |
| Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on… | 2025 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2025.10.20.683304v1) |
| Multitask benchmarking of single-cell multimodal omics integration methods | 2025 | Nature Methods | — | [link](https://www.nature.com/articles/s41592-025-02856-3) |
| BMFM-RNA: An Open Framework for Building and Evaluating Transcriptomic Foundation Models | 2025 | arXiv | Open framework for building/evaluating transcriptomic FMs. | [link](https://arxiv.org/abs/2506.14861) |
| Biology-driven insights into the power of single-cell foundation models | 2025 | Genome Biology | — | [link](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-025-03781-6) |
| Benchmarking gene embeddings from sequence, expression, network, and text models for func… | 2025 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2025.01.29.635607v1) |
| Diversity by Design: Addressing Mode Collapse Improves scRNA-seq Perturbation Modeling on… | 2025 | arXiv | — | [link](https://arxiv.org/abs/2506.22641) |
| Zero-shot evaluation reveals limitations of single-cell foundation models | 2025 | Genome Biology | — | [link](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-025-03574-x) |
| scDrugMap: benchmarking large foundation models for drug response prediction | 2025 | Nature Communicatio… | — | [link](https://www.nature.com/articles/s41467-025-67481-2) |
| A Systematic Evaluation of Single-Cell Foundation Models on Cell-Type Classification Task | 2025 | WSDM | — | [link](https://dl.acm.org/doi/10.1145/3701551.3708811) |
| Systema: a framework for evaluating genetic perturbation response prediction beyond syste… | 2025 | Nature Biotechnology | — | [link](https://www.nature.com/articles/s41587-025-02777-8) |
| Single Cell Foundation Models Evaluation (scFME) for In-Silico Perturbation | 2025 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2025.09.22.677811v1) |
| Deep-learning-based gene perturbation effect prediction does not yet outperform simple li… | 2025 | Nature Methods | — | [link](https://www.nature.com/articles/s41592-025-02772-6) |
| Benchmarking AI Models for in Silico Gene Perturbation of Cells | 2025 | bioRxiv | — | [link](https://doi.org/10.1101/2024.12.20.629581) |
| Benchmarking Machine Learning Models for Cellular Perturbation Analysis | 2025 | NeurIPS Datasets an… | — | [link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/8aee537279a66ced96319dfca3c00002-Abstract-Datasets_and_Benchmarks_Track.html) |
| Limitations of Cell Embedding Metrics Assessed Using Drifting Islands | 2025 | Nature Biotechnology | — | [link](https://doi.org/10.1038/s41587-025-02702-z) |
| Benchmarking and Evaluation of AI Models in Biology: Outcomes and Recommendations from th… | 2025 | arXiv | — | [link](https://arxiv.org/abs/2507.10502) |
| From Virtual Cell Challenge to Virtual Organs: Navigating the Deep Waters of Medical AI M… | 2025 | iCell | — | [link](https://doi.org/10.71373/IQHA9494) |
| Evaluating the utilities of foundation models in single-cell data analysis | 2024 | bioRxiv | — | — |
| Delineating the effective use of self-supervised learning in single-cell genomics | 2024 | Nature Machine Inte… | — | [link](https://www.nature.com/articles/s42256-024-00934-3) |
| BioLLM: A standardized framework for integrating and benchmarking single-cell foundation… | 2024 | Patterns | — | [link](https://www.sciencedirect.com/science/article/pii/S2666389925001746) |
| Evaluating the role of pre-training dataset size and diversity on single-cell foundation… | 2024 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2024.12.13.628448v1) |
| Metric Mirages in Cell Embeddings | 2024 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2024.04.02.587824v1) |
| PertEval-scFM: Benchmarking Single-Cell Foundation Models for Perturbation Effect Predict… | 2024 | ICML | — | [link](https://openreview.net/forum?id=t04D9bkKUq) |
| Benchmarking Transcriptomics Foundation Models for Perturbation Analysis: one PCA still r… | 2024 | arXiv | — | [link](https://arxiv.org/abs/2410.13956) |
| A Deep Dive into Single-Cell RNA Sequencing Foundation Models | 2023 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2023.10.19.563100v1) |
| Foundation Models Meet Imbalanced Single-Cell Data When Learning Cell Type Annotations | 2023 | bioRxiv | — | [link](https://www.biorxiv.org/content/10.1101/2023.10.24.563625v1) |
| MVCBench: A Multimodal Benchmark for Drug-induced Virtual Cell Phenotypes |  | bioRxiv | — | [link](https://www.biorxiv.org/content/10.64898/2026.04.22.720110v1) |

## Datasets & Atlases

| Title | Year | Venue | Notes | Links |
|---|---|---|---|---|
| Spatial Perturb-seq: Spatial perturb-seq data for functional genomics within intact tissu… | 2026 | — | — | [link](https://www.nature.com/articles/s41467-026-69677-6) |
| ProtiCelli: Proteome-wide image generation resources for human cell protein localization | 2026 | — | — | [link](https://doi.org/10.64898/2026.03.31.715748) |
| Tahoe-100M: Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent… | 2025 | — | — | [link](https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1) |
| X-Atlas/Orion: Genome-Wide Perturb-Seq Datasets via a Scalable Fix-Cryopreserve Platform… | 2025 | — | — | [link](https://www.biorxiv.org/content/10.1101/2025.06.11.659105v1) |
| CIGS: High-Throughput Profiling of Chemical-Induced Gene Expression across 93,644 Perturb… | 2025 | — | — | [link](https://www.nature.com/articles/s41592-025-02781-5) |
| scBaseCount: scBaseCount: An AI Agent-Curated, Uniformly Processed, and Continually Expan… | 2025 | — | — | [link](https://doi.org/10.1101/2025.02.27.640494) |
| CZ CELLxGENE Discover: A single-cell data platform for scalable exploration, analysis, an… | 2025 | — | — | [link](https://academic.oup.com/nar/article/53/D1/D886/7912032) |
| scGeneScope: scGeneScope: A Treatment-Matched Single Cell Imaging and Transcriptomics Dat… | 2025 | — | — | [link](https://openreview.net/forum?id=918POZbZ50) |
| Perturb-FISH: CRISPR screening with imaging-based spatial transcriptomics | 2025 | — | — | [link](https://doi.org/10.1016/j.cell.2025.02.012) |
| SubCell: Proteome-aware microscopy foundation model resources based on HPA images | 2025 | — | — | [link](https://doi.org/10.1101/2024.12.06.627299) |
| scPerturb: scPerturb: Harmonized Single-Cell Perturbation Data | 2024 | — | — | [link](https://www.nature.com/articles/s41592-023-02144-y) |
| CPJUMP1: Three million images and morphological profiles of cells treated with matched ch… | 2024 | — | — | [link](https://www.nature.com/articles/s41592-024-02241-6) |
| CM4AI: Cell Maps for Artificial Intelligence: AI-Ready Maps of Human Cell Architecture fr… | 2024 | — | — | [link](https://doi.org/10.1101/2024.05.21.589311) |
| HEST-1k: HEST-1k: A Dataset for Spatial Transcriptomics and Histology Image Analysis | 2024 | — | — | [link](https://arxiv.org/abs/2406.16192) |
| Tabula Sapiens: A multiple-organ single-cell transcriptomic atlas of humans | 2022 | — | — | [link](https://www.science.org/doi/10.1126/science.abl4896) |
| OpenCell: Endogenous protein tagging, localization, and interaction data for human cellul… | 2022 | — | — | [link](https://doi.org/10.1126/science.abi6983) |
| Sci-Plex: Massively Multiplex Chemical Transcriptomics at Single-Cell Resolution | 2019 | — | — | [link](https://doi.org/10.1126/science.aax6234) |
| L1000/CMap: A Next Generation Connectivity Map: L1000 Platform and the First 1,000,000 Pr… | 2017 | — | — | [link](https://doi.org/10.1016/j.cell.2017.10.049) |
| Drug Repurposing Hub: Curated compound library with targets, mechanisms, and clinical ann… | 2017 | — | — | [link](https://www.nature.com/articles/nm.4306) |
| Arc Virtual Cell Atlas: Large-scale perturbation atlas and codebase from Arc Institute [[… |  | — | — | [link](https://arcinstitute.org/tools/virtualcellatlas) |
| Perturb-seq datasets: Genome-scale and combinatorial Perturb-seq datasets from Replogle,… |  | — | — | [link](https://github.com/sanderlab/scPerturb) |
| Virtual Cell Challenge: Community perturbation-prediction challenge and hidden evaluation… |  | — | — | [link](https://virtualcellchallenge.org/) |
| Human Cell Atlas: International atlas of human cells and tissues [[portal](https://data.h… |  | — | — | [link](https://data.humancellatlas.org/) |
| Human BioMolecular Atlas Program: HuBMAP healthy human tissue atlas and common coordinate… |  | — | — | [link](https://hubmapconsortium.org/) |
| GTEx: Genotype-Tissue Expression project for human tissue expression baselines [[portal](… |  | — | — | [link](https://gtexportal.org/) |
| Cell Painting Gallery: Public high-content cell painting datasets from Broad and partners… |  | — | — | [link](https://registry.opendata.aws/cellpainting-gallery/) |
| RxRx: Recursion high-content cellular imaging datasets for perturbation and batch-correct… |  | — | — | [link](https://www.rxrx.ai/datasets) |
| 10x Genomics spatial datasets: Visium, Xenium, and related public spatial transcriptomics… |  | — | — | [link](https://www.10xgenomics.com/datasets) |
| Vizgen MERFISH datasets: Public MERFISH example datasets for spatial transcriptomics [[da… |  | — | — | [link](https://vizgen.com/data-release-program/) |
| Human Protein Atlas: Subcellular and tissue protein expression atlases [[resource](https:… |  | — | — | [link](https://www.proteinatlas.org/) |
| STRING: Protein functional association and interaction networks [[resource](https://strin… |  | — | — | [link](https://string-db.org/) |
| OmniPath: Signaling, ligand-receptor, and causal network priors for multi-omics analysis… |  | — | — | [link](https://omnipathdb.org/) |
| DepMap/CCLE/PRISM: Cancer dependency, molecular profile, and drug-response resources for… |  | — | — | [link](https://depmap.org/portal/) |
| ChEMBL: Drug-like molecules, bioactivities, targets, and assays [[resource](https://www.e… |  | — | — | [link](https://www.ebi.ac.uk/chembl/) |
| BindingDB: Protein-small molecule binding affinity knowledgebase [[resource](https://www.… |  | — | — | [link](https://www.bindingdb.org/) |
| PubChem: Compound identifiers, structures, assays, and bioactivity records [[resource](ht… |  | — | — | [link](https://pubchem.ncbi.nlm.nih.gov/) |

## Tools & Software

| Title | Year | Venue | Notes | Links |
|---|---|---|---|---|
| Large-scale proteome inference from unpaired single-cell transcriptomic and proteomic dat… | 2026 | Research Square | — | [link](https://doi.org/10.21203/rs.3.rs-9068677/v1) |
| STAMP: Single-cell transcriptomics analysis and multimodal profiling through imaging | 2025 | Cell | — | [link](https://doi.org/10.1016/j.cell.2025.05.027) |
| Multimodal learning enables chat-based exploration of single-cell data | 2025 | Nature Biotechnology | — | [link](https://www.nature.com/articles/s41587-025-02857-9) |
| Scvi-hub: An Actionable Repository for Model-Driven Single-Cell Analysis | 2025 | Nature Methods | — | [link](https://doi.org/10.1038/s41592-025-02799-9) |
| Pertpy: an End-to-end Framework for Perturbation Analysis |  | Nature Methods | — | [link](https://www.nature.com/articles/s41592-025-02909-7) |

## Perspectives & Surveys

| Title | Year | Venue | Notes | Links |
|---|---|---|---|---|
| Minimal life by computer. Nat Biotechnol (2026). https://doi.org/10.1038/s41587-026-03110… | 2026 | — | — | [link](https://doi.org/10.1038/s41587-026-03110-7) |
| Interpretation, extrapolation and perturbation of single cells | 2026 | Nature Reviews Gene… | — | [link](https://www.nature.com/articles/s41576-025-00920-4) |
| Build the virtual cell with artificial intelligence: a perspective for cancer research | 2025 | — | — | — |
| Unresolved questions in the application of artificial intelligence virtual cells for canc… | 2025 | — | — | — |
| Artificial Intelligence Virtual Cells: From Measurements to Decisions across Modality, Sc… | 2025 | arXiv | — | [link](https://arxiv.org/abs/2510.12498) |
| Virtual Cells as Causal World Models: A Perspective on Evaluation | 2025 | Cell | ICLR 2026 openreview paper Withdrawal by authors after comments | — |
| Virtual Cells: From Conceptual Frameworks to Biomedical Applications | 2025 | arXiv | — | [link](https://arxiv.org/abs/2509.18220) |
| Grow AI virtual cells: three data pillars and closed-loop learning | 2025 | Cell Research | propose here that the evolution or growth of AIVCs relies on three essential building blocks and nutrients: a priori knowledge, static architecture,… | — |
| AI-driven virtual cell models in preclinical research: technical pathways, validation mec… | 2025 | — | review outlines the technical pathways and validation mechanisms of virtual cells, emphasizing a closed-loop workflow from computational evaluation t… | — |
| Virtual cells: Predict, explain, discover | 2025 | arXiv | — | [link](https://arxiv.org/abs/2505.14613) |
| Large Language Models Meet Virtual Cell: A Survey | 2025 | arXiv | — | [link](https://arxiv.org/abs/2510.07706) |
| A survey on foundation language models for single-cell biology | 2025 | — | — | — |
| Single-cell foundation models: bringing artificial intelligence into cell biology | 2025 | — | — | — |
| Transformative advances in single-cell omics: a comprehensive review of foundation models… | 2025 | — | — | — |
| Towards multimodal foundation models in molecular cell biology | 2025 | Nature | — | [link](https://www.nature.com/articles/s41586-025-08710-y) |
| Overcoming barriers to the wide adoption of single-cell large language models in biomedic… | 2025 | Nature Methods | — | [link](https://www.nature.com/articles/s41587-025-02846-y) |
| Foundation models in bioinformatics | 2025 | National Science Re… | — | [link](https://academic.oup.com/nsr/article/12/4/nwaf028/7979309) |
| Transformers and genome language models | 2025 | Nature Machine Inte… | — | [link](https://www.nature.com/articles/s42256-025-01007-9) |
| How to build the virtual cell with artificial intelligence: Priorities and opportunities | 2024 | Cell | Main paper | — |
| The Human Cell Atlas: from a cell census to a unified foundation model | 2024 | Nature | — | [link](https://www.nature.com/articles/s41586-024-08338-4) |
| Harnessing the deep learning power of foundation models in single-cell omics | 2024 | Nature Reviews Mole… | — | [link](https://www.nature.com/articles/s41580-024-00756-6) |
| Transformers in single-cell omics: a review and new perspectives | 2024 | Nature Methods | — | [link](https://www.nature.com/articles/s41592-024-02353-z) |
| Toward a foundation model of causal cell and tissue biology with a Perturbation Cell and… | 2024 | Cell | — | [link](https://www.cell.com/cell/abstract/S0092-8674(24)00829-8) |
| From Equations to Agents: The Artificial Intelligence Virtual Cell Reshaping Precision On… |  | Cell | — | — |
| Towards Virtual Cell Construction by AI |  | Cell | — | — |

## Other Resources

| Title | Year | Venue | Notes | Links |
|---|---|---|---|---|
| Virtual Cells Need Context, Not Just Scale | 2026 | bioRxiv | — | — |
| Artificial intelligence-enabled multi-scale virtual cell: perspective, challenges, and op… | 2026 | Bioinformatics | — | — |
| Towards predictive virtual embryos with genomics and AI | 2026 | Nature Methods | — | — |
| What Makes a Representation Good for Single-Cell Perturbation Prediction? | 2026 | arXiv | — | [link](https://arxiv.org/abs/2605.19343) |
| Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Functi… | 2025 | bioRxiv | Giga-scale single-cell perturbation atlas (dataset). | [link](https://www.biorxiv.org/content/10.1101/2025.02.20.639398v3) |
| Toward ai-driven digital organism: Multiscale foundation models for predicting, simulatin… | 2024 | arXiv | — | [link](https://arxiv.org/abs/2412.06993) |
| Transcoder-based Circuit Analysis for Interpretable Single-Cell Foundation Models |  | arXiv | — | [link](https://arxiv.org/abs/2509.14723) |
| Foundation models improve perturbation response prediction |  | bioRxiv | Performed a comprehensive analysis of over 600 different models for embedding-based perturbation response prediction for both genetic and small molec… | [link](https://github.com/genbio-ai/foundation-models-perturbation) |
| Batch Effects Remain a Fundamental Barrier to Universal Embeddings in Single-Cell Foundat… |  | bioRxiv | — | — |

## Where to Publish & Track New Work

| Venue | Type | Notes | Link |
|---|---|---|---|
| LMRL Workshop @ ICLR | Workshop | The single best fit — explicitly built around virtual cells, with tracks on causality, generative modeling, and interpretable representations in biology Annual… | — |
| Mechanistic Interpretability Workshop @ ICML | Workshop | The flagship mech-interp venue (drew 600+ at NeurIPS 2025). Accepts short/long papers; fast-tracks accepted main-conf papers ICML 2026, Seoul, Jul 10; 2026 dea… | [link](https://mechinterpworkshop.com/) |
| MLCB (Machine Learning in Computational Biology) | Conference | Independent conference (ex-NeurIPS workshop), strong ML-for-biology audience; values mechanistic insight Nov 16–17, NY Genome Center; co-located near NeurIPS | [link](https://www.mlcb.org/) |
| ISMB / ISCB (incl. iscbAI track) | Conference | World's largest comp-bio conference; new dedicated AI track (iscbAI). Proceedings transferable to Bioinformatics Advances ISMB 2026, Washington DC; abstract de… | — |
| RECOMB | Conference | Top algorithmic comp-bio conference (peer of ISMB), rigorous review RECOMB 2026, Thessaloniki; paper deadline ~mid-Nov (prior year) | — |
| NeurIPS / ICLR / ICML main tracks | Conference | For methods-heavy scFM or interpretability contributions aimed at the core ML community | — |
| Re-Align Workshop @ ICML | Conference | Representational alignment + neural control; overlaps mech-interp; accepts concurrent submissions | [link](https://representational-alignment.github.io/2026/) |
| Nature Methods | Journal | Premier venue for new computational methods; has published scGPT, multimodal FM perspectives High bar; methods + benchmarking | — |
| Nature Communications | Journal | Broad; publishes interpretable scFMs (e.g., CellVQ) Good for full method + biology stories | [link](https://www.nature.com/ncomms/) |
| Cell / Cell Systems | Journal | Systems biology + virtual cell vision pieces; perturbation modeling Cell Systems is more method-friendly | — |
| Nature Reviews Genetics | Journal | Review/perspective on interpretation, extrapolation, perturbation of single cells For reviews/perspectives, not primary methods | — |
| Genome Biology | Journal | Strong single-cell methods home Open access | — |
| Bioinformatics / Bioinformatics Advances (OUP) | Journal | Core comp-bio methods; ISMB proceedings transfer here; OA option Faster turnaround | — |
| Experimental & Molecular Medicine | Journal | Published the major scFM review "bringing AI into cell biology" Good for reviews | [link](https://www.nature.com/emm/) |
| eLife | Journal | Reviewed-preprint model; biology + methods Public review process | [link](https://elifesciences.org/) |
| LLMs in drug discovery, genomics, single-cell ana… | Special issue | IEEE J. Biomedical & Health Informatics | — |
| Advances in Single-Cell & Spatial Transcriptomics… | Special issue | Bioinformatics (OUP) | — |
| Integrative Multi-Omics Approaches (Virtual Issue) | Special issue | Bioinformatics Advances (OUP) | — |
| CZI Virtual Cells benchmarking outputs | Special issue | Community (arXiv → journal) | — |

## Contributing

Add a row to the relevant CSV in [`data/`](data/) and run `python scripts/generate_readme.py`, then open a PR. Full instructions in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[CC0-1.0](LICENSE) — to the extent possible under law, contributors have waived all copyright to this curation. Linked papers remain under their own licenses.
