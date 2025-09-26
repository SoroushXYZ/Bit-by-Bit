# Bit-by-Bit AI Newsletter

An AI-generated tech newsletter that gathers data from RSS feeds, processes it with NLP/LLM pipelines, and curates high-quality technology news automatically.

## 🚀 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker, which includes all dependencies including Ollama:

```bash
# 1. Run the setup script
./docker-setup.sh

# 2. Run the complete pipeline
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py

# 3. Test the setup
./test-docker.sh
```

For detailed Docker instructions, see [DOCKER.md](DOCKER.md).

## 🏗️ Local Setup (Alternative)

If you prefer to run locally without Docker:

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
python pipeline/run_pipeline.py
```

## 📊 Pipeline Overview

The system processes tech news through 5 sequential steps:

1. **RSS Gathering** 📡 - Collects from 80+ tech RSS feeds
2. **Content Filtering** 🔍 - Language detection, word count, quality checks
3. **Ad Detection** 🚫 - Custom DistilBERT model filters advertisements
4. **LLM Quality Scoring** 🤖 - Ollama evaluates content quality (1-100 scale)
5. **Deduplication** 🔄 - Semantic similarity removes duplicate articles

## 🎯 Usage

### Run Complete Pipeline
```bash
# Docker
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py

# Local
python pipeline/run_pipeline.py
```

### Run Individual Steps
```bash
python pipeline/run_pipeline.py --step rss_gathering
python pipeline/run_pipeline.py --step content_filtering
python pipeline/run_pipeline.py --step ad_detection
python pipeline/run_pipeline.py --step llm_quality_scoring
python pipeline/run_pipeline.py --step deduplication
```

### Testing
```bash
python pipeline/tests/test_rss_gathering.py
python pipeline/tests/test_content_filtering.py
python pipeline/tests/test_ad_detection.py
python pipeline/tests/test_llm_quality_scoring.py
```

## 📁 Project Structure

```
Bit-by-Bit/
├── pipeline/               # Main processing pipeline
│   ├── config/            # JSON configuration files
│   ├── steps/             # Individual processing steps
│   ├── utils/             # Logging and config utilities
│   ├── tests/             # Test scripts
│   └── run_pipeline.py    # Main pipeline runner
├── research/              # Development and testing
│   ├── notebooks/         # Jupyter notebooks
│   └── data/              # Sample data
├── app/                   # Main application (future)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker orchestration
└── DOCKER.md              # Docker documentation
```

## 🔧 Configuration

The pipeline uses JSON configuration files in `pipeline/config/`:

- `pipeline_config.json` - Main pipeline settings
- `rss_feeds.json` - 80+ RSS feeds with categories and quality scores
- Individual step configurations for fine-tuning

## 📈 Features

- **80+ RSS Feeds**: Tech news, AI/ML, cloud, hardware, big tech
- **AI-Powered Processing**: DistilBERT ad detection, Ollama quality scoring
- **Semantic Deduplication**: Sentence transformers for similarity detection
- **Comprehensive Logging**: Detailed statistics and error handling
- **Modular Architecture**: Independent, configurable processing steps
- **Docker Ready**: Complete containerized environment

## 🎯 Current Status

✅ **Fully Functional Pipeline**
- Complete 5-step processing pipeline
- Comprehensive configuration system
- Error handling and logging
- Test suite for all components
- Docker containerization

🔄 **Next Steps**
- Newsletter template generation
- Image generation integration
- Publishing automation
- Web interface development

## 📚 Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker setup and usage guide
- [pipeline/README.md](pipeline/README.md) - Detailed pipeline documentation
- [research/README.md](research/README.md) - Research and development notes
