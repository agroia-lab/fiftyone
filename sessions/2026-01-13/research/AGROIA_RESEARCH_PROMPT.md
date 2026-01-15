# AgroIA Project Documentation & Change Log Prompt

> **Purpose**: Guide Claude Code to document the AgroIA project evolution, track changes over time, and maintain a living chronicle of development decisions and results.

---

## PROMPT START

You are documenting **AgroIA**, an evolving AI system for agricultural pesticide recommendations. Your role is to:

1. **Describe the project** as a complete system (architecture, goals, current state)
2. **Log all changes** with timestamps, context, and rationale
3. **Track evolution** from initial concept through current implementation
4. **Maintain living documentation** that grows with the project

---

## 1. Project Description Template

When describing AgroIA, use this structure:

### 1.1 Project Identity

```markdown
# AgroIA - Agricultural AI Companion

## Vision
{One sentence capturing the ultimate goal}
> "A trusted agricultural colleague that understands context, remembers history,
> and provides advice grounded in legal compliance and agronomic reality."

## Current Version: {X.Y.Z}
## Last Updated: {YYYY-MM-DD}
## Status: {Development | Testing | Production}

## Core Problem
{What problem does AgroIA solve? Why does it matter?}

## Key Innovation
{What makes AgroIA different from existing solutions?}
```

### 1.2 System Overview

```markdown
## Architecture Summary

┌─────────────────────────────────────────────────────────────┐
│                      AgroIA v{VERSION}                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DATA LAYER                                                 │
│  ├── {N} SAG-approved pesticide labels                     │
│  ├── Crops: {list crops}                                   │
│  └── Extraction: {method - e.g., Gold Standard V4}         │
│                                                             │
│  INTELLIGENCE LAYER                                         │
│  ├── LLM: {primary provider}                               │
│  ├── RAG: {vector store}                                   │
│  ├── Routing: {method}                                     │
│  └── Tools: {list tools}                                   │
│                                                             │
│  INTERFACE LAYER                                            │
│  ├── API: {framework, port}                                │
│  └── Frontend: {status}                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

## Current Capabilities
- [ ] {Capability 1} - {status}
- [ ] {Capability 2} - {status}
- [ ] {Capability 3} - {status}

## Known Limitations
- {Limitation 1}
- {Limitation 2}
```

---

## 2. Change Log System

### 2.1 Session Log Entry Template

For each work session, create an entry:

```markdown
# Session Log - {YYYY-MM-DD}

## Session Info
- **Date**: {YYYY-MM-DD}
- **Duration**: {X hours}
- **Version**: {before} → {after}
- **Focus**: {main topic}

## Changes Made

### Code Changes
| File | Change Type | Description |
|------|-------------|-------------|
| `{path}` | {add/modify/delete} | {what changed} |

### Configuration Changes
| Setting | Before | After | Reason |
|---------|--------|-------|--------|
| `{setting}` | `{old}` | `{new}` | {why} |

### Data Changes
- Labels added: {count}
- Labels verified: {count}
- Benchmark updated: {yes/no}

## Decisions Made
1. **Decision**: {what was decided}
   - **Context**: {why this came up}
   - **Options considered**: {alternatives}
   - **Rationale**: {why this choice}
   - **ADR**: {link if applicable}

## Results / Observations
- {observation 1}
- {observation 2}

## Next Steps
- [ ] {todo 1}
- [ ] {todo 2}

## Notes
{Any additional context for future reference}
```

### 2.2 Master Change Log Format

Maintain a master `CHANGELOG.md` at project root:

```markdown
# AgroIA Change Log

All notable changes to this project are documented here.

Format: [Semantic Versioning](https://semver.org/)
- MAJOR: Breaking changes or fundamental architecture shifts
- MINOR: New features, capabilities added
- PATCH: Bug fixes, refinements, documentation

---

## [Unreleased]
### Added
- {feature in progress}

### Changed
- {modification in progress}

---

## [0.4.0] - 2026-01-05
### Added
- Smart LLM Router with Anthropic Claude as primary
- 5-tier multi-tier routing system
- General expert pipeline for crop-agnostic queries
- Session context for follow-up queries
- ADR-001: Context-aware routing
- ADR-002: Multi-tier routing system

### Changed
- Primary LLM provider: OpenAI → Anthropic
- Routing: keyword-only → 5-tier with context

### Performance
- Benchmark: 50.6% → 69.4% (+18.8%)
- Mix compatibility: 10% → 92%
- Adjuvants: 43% → 93%

---

## [0.3.1] - 2025-11-10
### Added
- V4 Gold Standard extraction schema
- Human-in-the-loop verification workflow
- 186 labels extracted (92% success rate)

### Fixed
- Dosage table parsing accuracy
- Unicode normalization issues

---

## [0.2.0] - 2025-08-20
### Added
- Initial RAG implementation
- ChromaDB vector store

### Discovered
- RAG Paradox: PDF chunking degrades performance
- Score dropped from 3.96 → 2.68 with naive RAG

---

## [0.1.0] - 2025-05-15
### Added
- Initial project structure
- Basic GPT-4o integration
- First benchmark (20 questions)
```

---

## 3. Evolution Tracking

### 3.1 Architecture Evolution Document

Track how the system design evolved:

```markdown
# AgroIA Architecture Evolution

## Timeline

### Phase 1: Naive RAG (2025-05 to 2025-08)
**Approach**: Open WebUI + PDF chunk RAG
**Result**: FAILED - Performance degraded vs base model
**Learning**: Structured data needs structured extraction

### Phase 2: Gold Standard + Agentic (2025-08 to 2026-01)
**Approach**: Human-verified JSON + multi-tool orchestration
**Result**: SUCCESS - +18.8% improvement
**Current**: v0.4.0

### Phase 3: Hierarchical MoE (Planned)
**Approach**: Orchestrator + specialist agents + Cognee memory
**Goal**: True "companion" behavior
**Status**: Design phase

## Key Pivots

| Date | From | To | Trigger | Result |
|------|------|-----|---------|--------|
| 2025-08 | PDF RAG | Gold Standard | RAG Paradox discovery | +32% accuracy |
| 2026-01 | OpenAI | Anthropic | Cost + quality | Better routing |
| 2026-01 | Keyword routing | 5-tier | Follow-up failures | Context retention |

## Lessons Learned
1. {lesson 1}
2. {lesson 2}
```

### 3.2 Metrics History

Track key metrics over time:

```csv
# metrics_history.csv
date,version,benchmark_score,labels_extracted,labels_verified,model,notes
2025-05-15,0.1.0,3.96,0,0,gpt-4o,Baseline - no RAG
2025-06-01,0.1.1,2.68,50,0,gpt-4o,PDF RAG - degraded performance
2025-08-20,0.2.0,3.45,100,60,gpt-4o,First Gold Standard
2025-11-10,0.3.1,3.96,186,150,gpt-4o,V4 schema complete
2026-01-05,0.4.0,4.17,186,186,claude-sonnet,Agentic + smart routing
```

---

## 4. Documentation Updates

### 4.1 When to Update CLAUDE.md

Update the main `CLAUDE.md` when:
- [ ] Version number changes
- [ ] Architecture changes significantly
- [ ] New capabilities added
- [ ] New limitations discovered
- [ ] Key decisions made (add to ADRs)
- [ ] Benchmark results change significantly

### 4.2 CLAUDE.md Section Updates

```markdown
## Sections to Update

### Project Status & Strategy
- Current phase
- Completion percentages
- Roadmap checkboxes

### System Architecture
- Version number
- Layer descriptions
- Technology stack

### Known Issues & Limitations
- New issues discovered
- Issues resolved

### Changelog (bottom of CLAUDE.md)
- Add entry for significant changes
```

---

## 5. Session Workflow

### Starting a Session

```bash
# 1. Check current state
cat VERSION
cat torre_de_control/evaluation_metadata.json | jq '.current_status'

# 2. Review recent changes
git log --oneline -10

# 3. Create session log
echo "# Session Log - $(date +%Y-%m-%d)" > work_log/session_$(date +%Y-%m-%d).md
```

### During Session

```markdown
## Log as you work:

1. Before making changes:
   - Note current state
   - Document why change is needed

2. After making changes:
   - Document what changed
   - Note any unexpected results
   - Update relevant docs

3. If making decisions:
   - Create ADR if significant
   - Log rationale in session notes
```

### Ending a Session

```bash
# 1. Update VERSION if needed
echo "0.4.1" > VERSION

# 2. Update CHANGELOG.md
# Add entry under [Unreleased] or create new version section

# 3. Update torre_de_control/evaluation_metadata.json
# Add health_history entry

# 4. Update CLAUDE.md if significant changes

# 5. Commit with descriptive message
git add -A
git commit -m "Session $(date +%Y-%m-%d): {summary of changes}"
```

---

## 6. Quick Reference Commands

```bash
# View project status
cat VERSION && cat torre_de_control/evaluation_metadata.json | jq '.current_status'

# View recent changes
git log --oneline -20

# View architecture decisions
ls docs/architecture/decisions/

# Run benchmark and log
docker compose exec fastapi-pipeline python tools/benchmark/benchmark_runner.py

# Update Notion (Torre de Control)
python -c "from services.notion import NotionClient; NotionClient().full_sync()"

# Search for TODOs in code
grep -r "TODO\|FIXME\|XXX" --include="*.py" .
```

---

## 7. LaTeX Book Structure

### 7.1 Book Organization

AgroIA documentation is structured as a **book** with parts and chapters. Each chapter covers a specific module and links to associated research papers.

```
{AGROIA_ROOT}/docs/book/
├── main.tex                        # Main book document
├── main.pdf                        # Compiled book (versioned)
├── CHANGELOG.txt                   # Book version history
├── releases/                       # Archived PDF versions
│
├── frontmatter/
│   ├── titlepage.tex               # Title, authors, institution
│   ├── preface.tex                 # Project motivation
│   └── acknowledgments.tex         # Funding, collaborators
│
├── chapters/
│   │
│   │── part1_foundations/
│   │   ├── ch01_introduction.tex   # Vision, problem, philosophy
│   │   ├── ch02_domain.tex         # Agricultural context, Chile
│   │   └── ch03_related_work.tex   # Literature review
│   │
│   │── part2_architecture/
│   │   ├── ch04_system_overview.tex    # 3-layer architecture
│   │   ├── ch05_data_layer.tex         # Gold Standard extraction
│   │   ├── ch06_intelligence_layer.tex # LLM, RAG, routing
│   │   └── ch07_interface_layer.tex    # API, frontend
│   │
│   │── part3_modules/
│   │   ├── ch08_extraction.tex     # Label extraction pipeline
│   │   ├── ch09_rag_system.tex     # Vector store, retrieval
│   │   ├── ch10_routing.tex        # Multi-tier routing
│   │   ├── ch11_agents.tex         # Agentic architecture
│   │   └── ch12_memory.tex         # Session + long-term (Cognee)
│   │
│   │── part4_evaluation/
│   │   ├── ch13_benchmark.tex      # 4-level benchmark system
│   │   ├── ch14_rag_paradox.tex    # RAG failure analysis ← PAPER 1
│   │   └── ch15_results.tex        # Performance metrics
│   │
│   │── part5_evolution/
│   │   ├── ch16_timeline.tex       # Project evolution
│   │   ├── ch17_decisions.tex      # ADRs compilation
│   │   └── ch18_roadmap.tex        # Future plans
│   │
│   └── part6_appendices/
│       ├── appA_observations.tex   # Living observation log
│       ├── appB_technical.tex      # Commands, configs
│       ├── appC_schemas.tex        # JSON schemas, data formats
│       └── appD_glossary.tex       # Terms, abbreviations
│
└── figures/
    ├── architecture/
    ├── benchmarks/
    ├── evolution/
    └── modules/
```

### 7.2 Chapter-Paper Mapping

Each chapter can spawn or contribute to specific research papers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAPTER → PAPER MAPPING                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CHAPTER                          ASSOCIATED PAPER                  │
│  ─────────────────────────────────────────────────────────────────  │
│  Ch.05 Data Layer (Gold Standard) → Paper 2: Extraction Methodology │
│  Ch.08 Extraction Pipeline        →                                 │
│                                                                     │
│  Ch.14 RAG Paradox               → Paper 1: RAG Paradox Validation  │
│  Ch.09 RAG System                →    (Primary contribution)        │
│                                                                     │
│  Ch.10 Routing                   → Paper 3: Context-Aware Routing   │
│  Ch.11 Agents                    →    (Future)                      │
│  Ch.12 Memory                    →                                  │
│                                                                     │
│  Ch.13 Benchmark                 → Paper 4: Agricultural AI Eval    │
│  Ch.15 Results                   →    (Benchmark methodology)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.3 main.tex Book Template

```latex
\documentclass[11pt,a4paper,openany]{book}

% === PACKAGES ===
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,english]{babel}
\usepackage{geometry}
\geometry{margin=2.5cm}

% Graphics
\usepackage{graphicx}
\usepackage{float}
\usepackage{subcaption}
\graphicspath{{figures/}}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}

% Code listings
\usepackage{listings}
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    language=Python
}

% Links and references
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

% Bibliography
\usepackage{natbib}
\bibliographystyle{apalike}

% Headers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO]{\rightmark}
\fancyhead[RE]{\leftmark}
\fancyfoot[C]{AgroIA Documentation v\docversion}

% === VERSION INFO ===
\newcommand{\docversion}{0.4.0}
\newcommand{\docdate}{January 2026}

% === CUSTOM COMMANDS ===
\usepackage{xcolor}
\definecolor{observation}{RGB}{39,174,96}
\definecolor{decision}{RGB}{41,128,185}
\definecolor{warning}{RGB}{231,76,60}
\definecolor{milestone}{RGB}{142,68,173}
\definecolor{paperlink}{RGB}{155,89,182}

% Annotations
\newcommand{\obs}[2]{\textcolor{observation}{\textbf{[#1]} #2}}
\newcommand{\adr}[2]{\textcolor{decision}{\textbf{[ADR-#1]} #2}}
\newcommand{\warn}[1]{\textcolor{warning}{\textbf{[!]} #1}}
\newcommand{\mstone}[1]{\textcolor{milestone}{\textbf{[M]} #1}}

% Paper reference box
\newcommand{\paperref}[3]{%
    \begin{tcolorbox}[colback=paperlink!5,colframe=paperlink!50,title=Associated Paper]
    \textbf{#1}\\
    \textit{Status:} #2\\
    \textit{Target:} #3
    \end{tcolorbox}
}

% Chapter summary box
\usepackage{tcolorbox}
\newcommand{\chaptersummary}[1]{%
    \begin{tcolorbox}[colback=blue!5,colframe=blue!50,title=Chapter Summary]
    #1
    \end{tcolorbox}
}

% === DOCUMENT INFO ===
\title{
    \Huge\textbf{AgroIA}\\[0.5cm]
    \LARGE Agricultural AI Companion for\\
    Pesticide Recommendations\\[1cm]
    \large Project Documentation \& Research Compendium\\[0.5cm]
    \normalsize Version \docversion
}
\author{
    INIA Chile\\
    Weed Science \& Technology Program\\[0.5cm]
    \small Contact: lleon@inia.cl
}
\date{\docdate}

% === DOCUMENT ===
\begin{document}

% --- FRONT MATTER ---
\frontmatter
\maketitle
\input{frontmatter/preface}
\tableofcontents
\listoffigures
\listoftables

% --- MAIN MATTER ---
\mainmatter

% PART I: FOUNDATIONS
\part{Foundations}
\input{chapters/part1_foundations/ch01_introduction}
\input{chapters/part1_foundations/ch02_domain}
\input{chapters/part1_foundations/ch03_related_work}

% PART II: ARCHITECTURE
\part{System Architecture}
\input{chapters/part2_architecture/ch04_system_overview}
\input{chapters/part2_architecture/ch05_data_layer}
\input{chapters/part2_architecture/ch06_intelligence_layer}
\input{chapters/part2_architecture/ch07_interface_layer}

% PART III: MODULES
\part{Core Modules}
\input{chapters/part3_modules/ch08_extraction}
\input{chapters/part3_modules/ch09_rag_system}
\input{chapters/part3_modules/ch10_routing}
\input{chapters/part3_modules/ch11_agents}
\input{chapters/part3_modules/ch12_memory}

% PART IV: EVALUATION
\part{Evaluation \& Results}
\input{chapters/part4_evaluation/ch13_benchmark}
\input{chapters/part4_evaluation/ch14_rag_paradox}
\input{chapters/part4_evaluation/ch15_results}

% PART V: EVOLUTION
\part{Project Evolution}
\input{chapters/part5_evolution/ch16_timeline}
\input{chapters/part5_evolution/ch17_decisions}
\input{chapters/part5_evolution/ch18_roadmap}

% --- BACK MATTER ---
\backmatter

% APPENDICES
\appendix
\part{Appendices}
\input{chapters/part6_appendices/appA_observations}
\input{chapters/part6_appendices/appB_technical}
\input{chapters/part6_appendices/appC_schemas}
\input{chapters/part6_appendices/appD_glossary}

% BIBLIOGRAPHY
\bibliography{references}

\end{document}
```

### 7.4 Chapter Templates

#### ch01_introduction.tex
```latex
\chapter{Introduction}
\label{ch:introduction}

\chaptersummary{
This chapter presents the AgroIA vision, the problem it solves,
and the guiding philosophy of building an agricultural \textit{companion}
rather than a simple chatbot.
}

\section{Vision}

\begin{quote}
\textit{"A trusted agricultural colleague that understands context,
remembers history, and provides advice grounded in legal compliance
and agronomic reality."}
\end{quote}

AgroIA is not a chatbot. It is designed as a companion...

\section{The Problem}

Weed control decisions in Chilean agriculture face multiple challenges:
\begin{itemize}
    \item 186+ registered pesticide products with complex labels
    \item Legal responsibility for correct application
    \item Context-dependent recommendations (crop, phenology, weather)
    \item Resistance management requirements
\end{itemize}

\section{Design Philosophy}

\subsection{Companion, Not Tool}
% ...

\subsection{Sacred vs Evolving Data}
% ...

\subsection{System Humility}
% ...
```

#### ch14_rag_paradox.tex (Paper-linked chapter)
```latex
\chapter{The RAG Paradox}
\label{ch:rag_paradox}

\paperref{Paper 1: RAG Paradox Validation}{Draft v0.6}{Computers and Electronics in Agriculture}

\chaptersummary{
This chapter documents our critical discovery: naive PDF-based RAG
\textit{degrades} LLM performance for structured agricultural data.
This finding led to the Gold Standard extraction methodology.
}

\section{Background}

Initial implementation (May 2025) used Open WebUI with PDF chunk RAG...

\section{Experiment Design}

\subsection{Hypothesis}
Simple RAG over PDF chunks will degrade performance compared to
the base model's parametric knowledge.

\subsection{Methodology}
\begin{table}[H]
\centering
\caption{RAG Paradox Experiment Configuration}
\begin{tabular}{lll}
\toprule
\textbf{Condition} & \textbf{Baseline} & \textbf{Treatment} \\
\midrule
Model & GPT-4o & GPT-4o \\
RAG & Disabled & PDF chunks \\
Chunking & N/A & pdfplumber, 1000 tokens \\
Questions & 20 & 20 \\
\bottomrule
\end{tabular}
\end{table}

\section{Results}

\mstone{Critical Discovery - August 2025}

\begin{table}[H]
\centering
\caption{RAG Paradox Results}
\begin{tabular}{lccc}
\toprule
\textbf{Configuration} & \textbf{Score (5.0)} & \textbf{Passed} & \textbf{Dosage Acc.} \\
\midrule
GPT-4o (no RAG) & 3.96 & 14/20 & 45\% \\
GPT-4o + PDF RAG & 2.68 & 8/20 & 18\% \\
\textbf{Delta} & \textbf{-1.28} & \textbf{-6} & \textbf{-27\%} \\
\bottomrule
\end{tabular}
\end{table}

\section{Root Cause Analysis}

The performance degradation was traced to:
\begin{enumerate}
    \item \textbf{Table fragmentation}: pdfplumber split dosage tables mid-row
    \item \textbf{Context loss}: Numbers appeared without units or crop context
    \item \textbf{Semantic confusion}: LLM couldn't distinguish between crops
\end{enumerate}

\section{Implications}

\obs{2025-08-20}{This discovery validated the need for structured
extraction with human verification—the Gold Standard approach.}

\section{Related Paper}

This chapter forms the core of \textbf{Paper 1}:

\begin{itemize}
    \item \textbf{Title}: "The RAG Paradox: When Retrieval Augmentation
          Degrades Agricultural AI Performance"
    \item \textbf{Contribution}: Empirical validation with agricultural data
    \item \textbf{Status}: Draft v0.6, targeting submission Q1 2026
    \item \textbf{Location}: \texttt{docs/publications/paper\_1\_rag\_paradox/}
\end{itemize}
```

#### appA_observations.tex (Living Appendix)
```latex
\chapter{Observations Log}
\label{app:observations}

\textit{This appendix is append-only. New observations are added
chronologically, newest first. Each entry includes date and context.}

\section*{2026}

\subsection*{January 2026}

\obs{2026-01-14}{Book structure adopted for documentation. Each chapter
now maps to potential research papers, enabling modular publication.}

\obs{2026-01-05}{Anthropic Claude selected as primary LLM. Better
reasoning for agricultural domain at comparable cost to GPT-4o.}

\obs{2026-01-05}{5-tier routing implemented. Session context (T1)
enables follow-up queries like "Y en preemergencia?" without
re-specifying crop.}

\subsection*{December 2025}

\obs{2025-12-15}{L4 benchmark questions (context integration) remain
the weakest category. Requires relationship reasoning—target for
Cognee integration.}

\section*{2025}

\subsection*{November 2025}

\mstone{V4 Gold Standard Complete}

\obs{2025-11-10}{All 186 labels extracted and verified. Schema V4
is production-ready. 92\% automated extraction success rate with
~10 min human verification per label.}

\subsection*{August 2025}

\mstone{RAG Paradox Discovery}

\obs{2025-08-20}{CRITICAL: PDF chunk RAG degraded performance from
3.96 to 2.68 (-32\%). Root cause: table fragmentation. This validates
the Gold Standard approach over naive RAG.}

\subsection*{May 2025}

\obs{2025-05-15}{Project initiated. First benchmark: 20 questions,
GPT-4o baseline score 3.96/5.0.}
```

### 7.5 Book CHANGELOG

```
================================================================================
CHANGELOG - AgroIA Project Book
================================================================================

[0.4.0] - 2026-01-14
--------------------
STRUCTURE:
- Converted from article to book format
- Organized into 6 parts, 18 chapters, 4 appendices
- Added chapter-paper mapping system

CONTENT:
- Ch.14 RAG Paradox: complete with experiment data
- Ch.10 Routing: 5-tier system documented
- AppA Observations: updated through Jan 2026

PAPERS:
- Paper 1 (RAG Paradox): linked to Ch.14, draft v0.6

---

[0.3.0] - 2025-11-15
--------------------
- Initial book structure drafted
- Part II Architecture documented
- Gold Standard (Ch.05) complete

================================================================================
```

### 7.6 Compilation Workflow

```bash
# === BOOK COMPILATION ===

cd docs/book

# Full compilation (book requires multiple passes)
pdflatex -interaction=nonstopmode main.tex
bibtex main  # If using bibliography
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# View result
xdg-open main.pdf

# === VERSION RELEASE ===

VERSION="0.4.0"
DATE=$(date +%Y%m%d)
cp main.pdf "releases/AgroIA_Book_v${VERSION}_${DATE}.pdf"

echo "Released: AgroIA_Book_v${VERSION}_${DATE}.pdf"
```

### 7.7 Chapter Update Guidelines

When updating specific chapters:

```markdown
## Update Triggers by Chapter

| Chapter | Update When... |
|---------|----------------|
| Ch.04 System Overview | Architecture changes |
| Ch.05 Data Layer | New extractions, schema changes |
| Ch.06 Intelligence | LLM provider changes, new models |
| Ch.10 Routing | Routing logic modified |
| Ch.13 Benchmark | New benchmark runs |
| Ch.14 RAG Paradox | Paper submission status changes |
| Ch.15 Results | Performance metrics change |
| Ch.16 Timeline | Major milestones reached |
| Ch.17 Decisions | New ADRs created |
| AppA Observations | Every session (append) |
```

---

## 8. Complete Session Workflow (Updated)

### Starting a Session

```bash
# 1. Check current state
cat VERSION
cat docs/project_documentation/CHANGELOG.txt | head -20

# 2. Review what needs updating
git log --oneline -10
cat torre_de_control/evaluation_metadata.json | jq '.current_status'
```

### During Session - Document as You Go

```markdown
## When making observations:
→ Add to sections/08_observations_log.tex (prepend, newest first)

## When making decisions:
→ Add ADR to sections/09_decisions_log.tex
→ Create full ADR in docs/architecture/decisions/ if significant

## When changing architecture:
→ Update sections/03_architecture.tex
→ Add to sections/04_evolution.tex timeline

## When running benchmarks:
→ Update sections/07_benchmarks.tex with new results
→ Add to metrics_history.csv
```

### Ending a Session

```bash
# 1. Update observations log with session findings
# Edit sections/08_observations_log.tex

# 2. Update CHANGELOG.txt for PDF
# Add entry under current version or create new version

# 3. Recompile PDF
cd docs/project_documentation
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# 4. If significant changes, bump version and archive
python tools/docs/update_documentation.py --version 0.4.1

# 5. Update project VERSION and CLAUDE.md if needed

# 6. Commit everything
git add -A
git commit -m "Session $(date +%Y-%m-%d): {summary}"
```

---

## PROMPT END

---

## Example Usage

When starting a work session on AgroIA:

```
I'm starting a work session on AgroIA.

Current version: 0.4.0
Focus today: {what you plan to work on}

Please:
1. Check current project state
2. Create session log entry
3. Document changes as we work
4. Update CHANGELOG and CLAUDE.md as needed

Reference AGROIA_RESEARCH_PROMPT.md for documentation standards.
```

When ending a session:

```
Session complete. Please:
1. Summarize changes made today
2. Update session log with results
3. Update CHANGELOG.md with new entries
4. Update VERSION if needed
5. Suggest CLAUDE.md updates if significant changes
```
