# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a coursework repository for **CERT x466-003: Data Storytelling** at the University of Minnesota. The main deliverable is a Jupyter notebook (`CERT-x466-003_MAIN.ipynb`) containing data analysis, visualizations, and assignment submissions. The final project is a self-chosen data story built over six weeks.

## Environment

This project uses `uv` for dependency management with Python 3.13.

```bash
# Install dependencies
uv sync

# Launch Jupyter Lab
uv run jupyter lab

# Launch classic Jupyter
uv run jupyter notebook

# Run a Python script
uv run python src/<script>.py
```

## Key Dependencies

- **pandas**, **numpy** — data manipulation
- **matplotlib**, **plotly** — visualization
- **scikit-learn**, **tensorflow** — ML (available for final project)
- **kaggle** — dataset retrieval

## GPU / CUDA Configuration

- **System GPU**: NVIDIA RTX 2080 Ti, CUDA 13.1 driver
- **PyTorch**: Installed from `pytorch-cu130` index (CUDA 13.0 wheels). Source in `[tool.uv.sources]`
- **TensorFlow**: Uses `tensorflow[and-cuda]` which installs cu12 nvidia pip packages. Requires `ctypes.CDLL` preloading in the notebook GPU ACCELERATION cell since Jupyter's running process won't pick up `LD_LIBRARY_PATH` changes
- **RAPIDS**: Installed as `cu12` packages from `nvidia-pypi` index. `cuml.accel` is **disabled** — cu12 JIT compilation fails against CUDA 13.1 system headers (`/opt/cuda/include/cuda_fp8.hpp`). Use `cuml` via direct imports instead. `cudf.pandas` works fine
- **uv version**: 0.8.11 (predates `torch-backend` config option from 0.9.18)

## Repository Structure

- `CERT-x466-003_MAIN.ipynb` — primary notebook for all assignments and analysis
- `data/` — datasets (`ai_job_market_dataset.csv`, `boot_ai_job_market_dataset.csv`)
- `docs/assignments/` — written assignment submissions in Markdown
- `models/` — saved model artifacts

## Workflow Notes

Assignment submissions go in `docs/assignments/` named `Logan-R-Sloan_CERT-x466-003_Assignment0X.md`. The main notebook is the primary workspace; `src/` holds supporting code kept out of the main notebook.
Assignment submission files use the suffix `_submission.md` (e.g., `Logan-R-Sloan_CERT-x466-003_Assignment03_submission.md`).

## Notebook Access

`CERT-x466-003_MAIN.ipynb` exceeds the Read tool's 10k token limit. To inspect it, parse as JSON via Bash:
```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
for i, c in enumerate(nb['cells']):
    print(f'[{i:3d}] {c[\"cell_type\"]:8s} | {chr(10).join(c[\"source\"])[:120]}')
"
```

## Notebook Structure (69 cells)

- **Cells 0–3**: Title and separators
- **Cells 4–6**: Kaggle dataset download
- **Cells 7–9**: GPU acceleration (cudf.pandas)
- **Cells 10–12**: Imports
- **Cells 13–21**: Dataset loading, shape (15,518 × 19), dtypes, nulls, nunique, describe
- **Cells 22–52**: **EDA** — 30 Plotly charts numbered 1–30 (salary distributions, experience trends, skills, seasonal hiring, entry-level-filtered views, etc.)
- **Cells 53–60**: **ML** — 6 models (salary prediction, experience classification, urgency, remote type, growth analysis, PyTorch Integrated Gradients)
- **Cells 61–66**: **Deep Learning** — entity embeddings, autoencoder anomaly detection
- **Cells 67–68**: DATA STORY section (placeholder)

## Package Index Configuration

`pyproject.toml` has two custom indexes — do not remove or rename:
- `pytorch-cu130` (explicit) — CUDA-enabled PyTorch wheels
- `nvidia-pypi` — RAPIDS/cuDF/cuML packages from `https://pypi.nvidia.com`

## Project Goals
- To use data visualization and data storytelling techniques to examine the `docs/boot_ai_job_market_dataset.csv` dataset to create a forecast of the future AI job market, primarily focusing on individuals planning to enter the job market with little to no work experience.

