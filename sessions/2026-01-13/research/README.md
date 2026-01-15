# Research Project: Semantic Clustering of Agricultural Drone Imagery

---

## Reusable Research Prompts

This project includes reusable prompts for Claude Code to replicate the research workflow:

| Prompt File | Purpose | Use Case |
|-------------|---------|----------|
| `RESEARCH_WORKFLOW_PROMPT.md` | Full workflow documentation | Reference for all procedures, code templates |
| `CLAUDE_RESEARCH_PROMPT.md` | Quick start for new projects | Copy and customize for new image analysis |
| `AGROIA_RESEARCH_PROMPT.md` | AgroIA project chronicle | Document project evolution, log changes over time |

### How to Use

1. **New drone/image project**: Copy `CLAUDE_RESEARCH_PROMPT.md`, fill in project details
2. **AgroIA research session**: Reference `AGROIA_RESEARCH_PROMPT.md` for paper writing
3. **Understanding procedures**: Read `RESEARCH_WORKFLOW_PROMPT.md` for complete documentation

---

## Project Structure

```
research/
├── paper/                    # LaTeX document
│   ├── main.tex             # Main document (compile this)
│   ├── sections/            # Modular content sections
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── objectives.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── conclusions.tex
│   │   ├── observations.tex # Living observation log
│   │   └── technical.tex    # Technical appendix
│   └── figures/             # All plots and visualizations
├── data/
│   ├── raw/                 # Original data (not tracked)
│   └── processed/           # Analysis-ready data
│       ├── santa_ines_data.csv
│       └── similarity_neighbors.csv
├── analysis/
│   ├── R/                   # R analysis scripts
│   │   ├── analysis.R
│   │   └── similarity_analysis.R
│   └── python/              # Python scripts
├── notes/                   # Working notes
└── logs/                    # Processing logs
```

## Quick Start

### Install LaTeX (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
```

### Compile Document

```bash
cd paper
pdflatex main.tex
pdflatex main.tex  # Run twice for table of contents

# Or use latexmk for automatic compilation
latexmk -pdf main.tex
```

### Run R Analysis

```bash
cd analysis/R
Rscript analysis.R
Rscript similarity_analysis.R
```

## Document Sections

| Section | File | Status | Description |
|---------|------|--------|-------------|
| Abstract | `abstract.tex` | Draft | Summary of findings |
| Introduction | `introduction.tex` | Draft | Background, research gap |
| Objectives | `objectives.tex` | Draft | Research questions, hypotheses |
| Methods | `methods.tex` | Draft | Data, tools, methodology |
| Results | `results.tex` | Draft | Figures, tables, findings |
| Discussion | `discussion.tex` | Draft | Interpretation, limitations |
| Conclusions | `conclusions.tex` | Draft | Key takeaways |
| Observations | `observations.tex` | Active | Living log of observations |
| Technical | `technical.tex` | Reference | Software versions, commands |

## Custom Commands

The LaTeX document includes annotation commands for draft mode:

- `\observation{text}` - Green: Observations during analysis
- `\finding{text}` - Blue: Key findings to highlight
- `\todo{text}` - Red: Items needing attention

## Updating the Document

1. **Add new results**: Edit `sections/results.tex`, add figures to `figures/`
2. **Log observations**: Append to `sections/observations.tex` with date
3. **Refine sections**: Each section is independent, edit as needed
4. **Recompile**: Run `pdflatex main.tex` twice

## Data Sources

- **FiftyOne dataset**: `santa_ines_dron` (97 drone images)
- **Brain keys**: `clip_viz` (embeddings), `clip_similarity` (similarity index)

## Generated Figures

| Figure | Description |
|--------|-------------|
| `r_embeddings_plot.png` | UMAP projection with category colors |
| `r_combined_analysis.png` | Labeled embeddings with outlier annotations |
| `r_similarity_network.png` | k-NN network visualization |
| `r_distance_distribution.png` | Within vs between-category distances |
| `r_cluster_cohesion.png` | Cluster tightness comparison |
| `r_size_analysis.png` | File size by category |
| `gps_vs_embeddings.png` | Comparison of spatial vs semantic clustering |
| `santa_ines_embeddings.png` | Original matplotlib embedding plot |
