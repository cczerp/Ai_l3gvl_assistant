# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip or conda
- 16GB+ RAM (for local models)
- GPU with 16GB+ VRAM (recommended for local models)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/cczerp/Ai_l3gvl_assistant.git
cd Ai_l3gvl_assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PINECONE_API_KEY=your_pinecone_key
API_SECRET_KEY=your_secret_key
```

### 5. Download Local Models (Optional)

For local model support:

```bash
# Create models directory
mkdir -p models

# Download Llama3 (example using huggingface-cli)
huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --local-dir models/llama3-8b-instruct

# Download Mixtral
huggingface-cli download mistralai/Mixtral-8x7B-Instruct-v0.1 --local-dir models/mixtral-8x7b-instruct
```

### 6. Initialize Data Directories

The data directories are already created. To populate with legal data:

```bash
# Example: Download state laws (user must provide data sources)
# Place state law files in: data/state_laws/{state}/
# Place federal laws in: data/federal_laws/
# Place cases in: data/cases/
# Place legal dictionaries in: data/legal_dictionaries/
```

### 7. Initialize Vector Store

```bash
python scripts/init_vector_store.py
```

## Running the Server

### Development Mode

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

## Ingesting Data

### Ingest All Data

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"doc_type": "all"}'
```

### Ingest Specific Data Type

```bash
# State laws for California
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"doc_type": "state_laws", "state": "CA"}'

# Federal laws
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"doc_type": "federal_laws"}'

# Cases from 2020-2024
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"doc_type": "cases", "start_year": 2020, "end_year": 2024}'
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Configuration

### Model Configuration

Edit `config/models.yaml` to configure models:

```yaml
cloud_models:
  openai:
    enabled: true
    model_name: "gpt-4"
    # ... other settings
```

### RAG Configuration

Edit `config/rag.yaml` to configure RAG settings:

```yaml
embeddings:
  model: "text-embedding-ada-002"
  dimension: 1536
  # ... other settings
```

### API Configuration

Edit `config/api.yaml` to configure API settings:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  # ... other settings
```

## Troubleshooting

### Out of Memory with Local Models

Reduce model size or use quantization:

```yaml
local_models:
  llama3:
    quantization: "4bit"  # or "8bit"
```

### Vector Store Issues

Clear and reinitialize:

```bash
rm -rf data/vector_store/*
python scripts/init_vector_store.py
```

### API Connection Issues

Check firewall settings and ensure port 8000 is open:

```bash
sudo ufw allow 8000
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
- Check [API.md](API.md) for API documentation
- See example scripts in `scripts/` directory
