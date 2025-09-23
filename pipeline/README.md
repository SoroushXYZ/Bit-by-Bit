# Bit-by-Bit Newsletter Pipeline

A modular, configurable pipeline for automated tech newsletter content processing.

## Structure

```
pipeline/
├── config/                 # Configuration files
│   ├── pipeline_config.json
│   ├── rss_gathering_config.json
│   └── rss_feeds.json
├── steps/                  # Pipeline steps
│   ├── __init__.py
│   └── rss_gathering.py
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── logger.py
│   └── config_loader.py
├── tests/                  # Test scripts
│   └── test_rss_gathering.py
├── logs/                   # Log files (gitignored)
├── data/                   # Data storage (gitignored)
│   ├── raw/               # Raw collected data
│   ├── processed/         # Processed data
│   └── output/            # Final output
├── run_pipeline.py        # Main pipeline runner
└── README.md              # This file
```

## Configuration

The pipeline uses JSON configuration files for maximum flexibility:

- `pipeline_config.json`: Main pipeline configuration
- `rss_gathering_config.json`: RSS gathering step configuration

## Usage

### Run the complete pipeline:
```bash
python pipeline/run_pipeline.py
```

### Run specific step:
```bash
python pipeline/run_pipeline.py --step rss_gathering
python pipeline/run_pipeline.py --step content_filtering
```

### Test individual steps:
```bash
python pipeline/tests/test_rss_gathering.py
python pipeline/tests/test_content_filtering.py
```

### Verbose logging:
```bash
python pipeline/run_pipeline.py --verbose
```

## Current Steps

### Step 1: RSS Gathering
- Collects raw RSS feed data from configured sources
- Handles errors gracefully with retry logic
- Supports parallel processing for better performance
- Saves raw data in JSON format with metadata

### Step 2: Content Filtering
- Filters articles by minimum word count (100 words)
- Language detection (English only)
- Basic quality checks (title length, URL presence)
- Excludes articles with poor content quality
- Provides detailed filtering statistics

## Features

- **Modular Design**: Each step is independent and configurable
- **Error Handling**: Graceful error handling with logging
- **Configuration Management**: JSON-based configuration system
- **Logging**: Comprehensive logging with rotation
- **Data Management**: Organized data storage structure
- **Parallel Processing**: Efficient RSS feed processing

## Dependencies

- feedparser
- requests
- Standard Python libraries

## Next Steps

The pipeline is designed to be extensible. Future steps will include:
- Content filtering and quality assessment
- Deduplication
- LLM-based analysis
- Newsletter generation
- Publishing
