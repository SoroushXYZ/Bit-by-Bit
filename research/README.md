# Research & Testing Area

This directory contains experimental scripts and notebooks for testing different tools and APIs before integrating them into the main application.

## Structure

```
research/
├── scripts/           # Python scripts for testing APIs and tools
├── notebooks/         # Jupyter notebooks for data exploration
├── data/             # Sample data and test outputs
└── README.md         # This file
```

## Current Research

### Data Sources
- **Guardian API** (`scripts/guardian_collector.py`) - Testing tech news collection
- More sources to be added...

### Testing Workflow
1. Create script in `scripts/` to test new tool/API
2. Use Jupyter notebooks in `notebooks/` for exploration
3. Save sample data in `data/` for analysis
4. Only integrate successful tools into main `app/`

## Guidelines

- Keep scripts simple and focused on one tool/API
- Document what works and what doesn't
- Save sample outputs for reference
- Don't commit sensitive data (API keys, etc.)
