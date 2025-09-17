# Research & Testing Area

This directory contains Jupyter notebooks for testing different tools and APIs before integrating them into the main application.

## Structure

```
research/
├── notebooks/         # Jupyter notebooks for data exploration and testing
├── data/             # Sample data and test outputs
│   └── guardian/     # Guardian API data (JSON format)
└── README.md         # This file
```

## Current Research

### Data Sources
- **Guardian API** (`notebooks/01_guardian_api_exploration.ipynb`) - Testing tech news collection
- More sources to be added...

### Testing Workflow
1. Create notebook in `notebooks/` to test new tool/API
2. Include all code directly in the notebook for better control
3. Save sample data in `data/{source_name}/` for analysis
4. Use JSON format for all data storage
5. Only integrate successful tools into main `app/`

## Guidelines

- Keep everything in notebooks for better control and data saving
- Use JSON format for all data storage (no CSV)
- Organize data by source in separate folders
- Document what works and what doesn't
- Save sample outputs for reference
- Don't commit sensitive data (API keys, etc.)
