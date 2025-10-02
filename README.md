# Bit-by-Bit AI Newsletter

An AI-powered tech newsletter that automatically gathers data from RSS feeds, GitHub trending, and stock markets, processes it through advanced NLP/LLM pipelines, and generates curated newsletters with intelligent grid layouts.

## 🚀 Quick Start

Local setup instructions:

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install and setup Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve &

# Pull required model
ollama pull llama3.2:3b
```

4. **Run the pipeline:**
```bash
cd pipeline && python run_pipeline.py
```

## 📊 Pipeline Overview

The system processes tech content through multiple data sources and intelligent processing steps:

### Data Collection 📡
- **RSS Gathering** - Collects from 80+ tech RSS feeds
- **GitHub Trending** - Fetches trending repositories and topics
- **Stock Data** - Gathers market data for tech companies

### Content Processing 🔍
1. **Content Filtering** - Language detection, word count, quality checks
2. **Ad Detection** - Custom DistilBERT model filters advertisements  
3. **LLM Quality Scoring** - Ollama evaluates content quality (1-100 scale)
4. **Deduplication** - Semantic similarity removes duplicate articles
5. **Article Prioritization** - Ranks content by relevance and quality
6. **Summarization** - AI-powered content summarization

### Newsletter Generation 📰
7. **Grid Layout** - Intelligent grid blueprint generation
8. **Data Filling** - Populates grid with processed content
9. **Newsletter Generation** - Creates final newsletter output

## 🎯 Usage

### Run Complete Pipeline
```bash
cd pipeline && python run_pipeline.py --step all
```

### Run Individual Steps
```bash
# Data Collection
python run_pipeline.py --step data_collection

# Processing Steps
python run_pipeline.py --step processing
python run_pipeline.py --step content_filtering
python run_pipeline.py --step ad_detection
python run_pipeline.py --step llm_quality_scoring
python run_pipeline.py --step deduplication
python run_pipeline.py --step article_prioritization
python run_pipeline.py --step summarization

# Newsletter Generation
python run_pipeline.py --step gridding
python run_pipeline.py --step data_filling
python run_pipeline.py --step newsletter_generation
```

### Output Structure
Each pipeline run creates an isolated directory with timestamp:
```
data/
└── YYYYMMDD_HHMMSS/          # Run-specific directory
    ├── raw/                   # Raw collected data
    │   ├── rss_raw.json
    │   ├── github_trending.json
    │   └── stock_data.json
    ├── processed/             # Processed content
    │   ├── filtered_content.json
    │   ├── ad_filtered_content.json
    │   ├── quality_scored_content.json
    │   ├── deduplicated_content.json
    │   ├── prioritized_content.json
    │   └── summarized_content.json
    ├── output/                # Final outputs
    │   ├── grid_blueprint.json
    │   ├── filled_grid_blueprint.json
    │   └── newsletter_output.json
    └── logs/                  # Run-specific logs
        └── pipeline.log
```

### Testing
```bash
cd pipeline
python -m pytest tests/ -v
```

## 📁 Project Structure

```
Bit-by-Bit/
├── pipeline/                    # Main processing pipeline
│   ├── src/                     # Source code
│   │   ├── data_collection/     # Data gathering modules
│   │   │   ├── rss_gathering.py
│   │   │   ├── github_trending.py
│   │   │   └── stock_data.py
│   │   ├── processing/          # Content processing steps
│   │   │   ├── content_filtering.py
│   │   │   ├── ad_detection.py
│   │   │   ├── llm_quality_scoring.py
│   │   │   ├── deduplication.py
│   │   │   ├── article_prioritization.py
│   │   │   ├── summarization.py
│   │   │   └── newsletter_generation.py
│   │   ├── gridding/            # Layout generation
│   │   │   ├── grid_placer.py
│   │   │   └── data_filler.py
│   │   └── utils/               # Utilities
│   │       ├── config_loader.py
│   │       └── logger.py
│   ├── config/                  # Configuration files
│   ├── data/                    # Run-specific output directories
│   ├── tests/                   # Test scripts
│   └── run_pipeline.py          # Main pipeline runner
├── research/                    # Development and testing
│   └── notebooks/               # Jupyter notebooks
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration

The pipeline uses JSON configuration files in `pipeline/config/`:

- `pipeline_config.json` - Main pipeline settings and step orchestration
- `global_config.json` - Global settings (API keys, model configs)
- `rss_feeds.json` - 80+ RSS feeds with categories and quality scores
- Individual step configurations for fine-tuning each processing stage

### Key Configuration Features
- **Run-Scoped Directories**: Each run creates isolated `data/<timestamp>/` folders
- **Flexible Step Execution**: Run individual steps or complete pipeline
- **AI Model Configuration**: Ollama settings, quality scoring parameters
- **RSS Feed Management**: Categorized feeds with quality weights

## 📈 Features

- **Multi-Source Data Collection**: RSS feeds, GitHub trending, stock data
- **AI-Powered Processing**: DistilBERT ad detection, Ollama quality scoring
- **Semantic Deduplication**: Sentence transformers for similarity detection
- **Intelligent Summarization**: AI-powered content summarization
- **Grid Layout System**: Automated newsletter layout generation
- **Run Isolation**: Each execution creates separate output directories
- **Comprehensive Logging**: Detailed statistics and error handling per run
- **Modular Architecture**: Independent, configurable processing steps
- **Easy Setup**: Simple Python virtual environment setup

## 🎯 Current Status

✅ **Production-Ready Pipeline**
- Complete 9-step processing pipeline with data collection, processing, and newsletter generation
- Run-scoped directory structure for complete isolation between executions
- Multi-source data integration (RSS, GitHub, stocks)
- AI-powered content curation and summarization
- Intelligent grid layout system
- Comprehensive configuration system
- Error handling and detailed logging
- Simple local setup with virtual environment

🔄 **Next Steps**
- Web interface for pipeline management
- Email newsletter distribution
- Advanced layout templates
- Real-time monitoring dashboard

## 📚 Documentation

- [pipeline/README_Docker.md](pipeline/README_Docker.md) - Docker setup and usage guide
- Configuration files in `pipeline/config/` - Detailed step-by-step settings
- Run logs in `pipeline/data/<run_id>/logs/` - Execution details and debugging info

## 🚀 Quick Examples

### Generate a Complete Newsletter
```bash
cd pipeline
python run_pipeline.py --step all
# Output: data/YYYYMMDD_HHMMSS/output/newsletter_output.json
```

### Process Only RSS Data
```bash
python run_pipeline.py --step data_collection
python run_pipeline.py --step processing
# Output: data/YYYYMMDD_HHMMSS/processed/summarized_content.json
```

### Create Grid Layout
```bash
python run_pipeline.py --step gridding
python run_pipeline.py --step data_filling
# Output: data/YYYYMMDD_HHMMSS/output/filled_grid_blueprint.json
```
