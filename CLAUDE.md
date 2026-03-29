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
- `src/` — helper scripts and auxiliary notebooks
- `models/` — saved model artifacts

## Workflow Notes

Assignment submissions go in `docs/assignments/` named `Logan-R-Sloan_CERT-x466-003_Assignment0X.md`. The main notebook is the primary workspace; `src/` holds supporting code kept out of the main notebook.

## Package Index Configuration

`pyproject.toml` has two custom indexes — do not remove or rename:
- `pytorch-cu130` (explicit) — CUDA-enabled PyTorch wheels
- `nvidia-pypi` — RAPIDS/cuDF/cuML packages from `https://pypi.nvidia.com`

## Project Goals
- To
