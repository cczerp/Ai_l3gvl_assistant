# Legal-AI Assistant

A hybrid legal-AI system combining cloud models (GPT-4, Claude) with local models (Llama3, Mixtral), featuring comprehensive RAG capabilities for legal research and analysis.

## Features

### 🤖 Hybrid Model Architecture
- **Cloud Models**: OpenAI GPT-4 and Anthropic Claude for complex legal reasoning
- **Local Models**: Llama3 and Mixtral for quick queries and cost optimization
- **Intelligent Router**: Automatically selects the best model based on query complexity and requirements

### 📚 Comprehensive Legal Data
- **50 State Laws**: Complete coverage of all U.S. state statutes
- **Federal Laws**: U.S. Code and federal regulations
- **50 Years of Case Law**: Historical case law from 1974-2024
- **Legal Dictionaries**: Comprehensive legal terminology database

### 🔍 RAG (Retrieval-Augmented Generation)
- Vector embeddings with FAISS, Pinecone, or Weaviate
- Semantic search with reranking
- Context-aware retrieval
- Metadata filtering by jurisdiction

### ✅ Citation Management
- Automatic citation extraction
- Citation validation and verification
- Multiple format support (Bluebook, ALWD)
- Parallel citation finding

### 🕸️ Precedent Graph
- Case relationship mapping
- Citation network analysis
- Precedent chain discovery
- Treatment tracking (followed, distinguished, overruled)

### 🔄 Data Ingestion Pipeline
- Automated document processing
- Metadata extraction
- Chunking with overlap
- Incremental updates

### 🚀 REST API
- FastAPI-based endpoints
- JWT authentication
- Rate limiting
- CORS support
- Comprehensive documentation

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/cczerp/Ai_l3gvl_assistant.git
cd Ai_l3gvl_assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run the Server

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

## Usage Examples

### Query Legal Question

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the requirements for a valid contract?",
    "jurisdiction": "federal",
    "use_rag": true
  }'
```

### Check Citations

```bash
curl -X POST "http://localhost:8000/api/v1/citation/check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Brown v. Board of Education, 347 U.S. 483"
  }'
```

### Search Precedent

```bash
curl -X POST "http://localhost:8000/api/v1/precedent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "contract law",
    "jurisdiction": "federal",
    "limit": 10
  }'
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           User Query                         │
└────────────────┬────────────────────────────┘
                 │
         ┌───────▼────────┐
         │  Model Router  │
         └───────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼───┐              ┌──────▼──────┐
│ Cloud │              │    Local    │
│Models │              │   Models    │
└───┬───┘              └──────┬──────┘
    │                         │
    └────────────┬────────────┘
                 │
         ┌───────▼────────┐
         │  RAG System    │
         └───────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────┐          ┌───────▼──────┐
│ Vector   │          │ Precedent    │
│  Store   │          │    Graph     │
└──────────┘          └──────────────┘
```

## Project Structure

```
Ai_l3gvl_assistant/
├── config/                  # Configuration files
│   ├── models.yaml         # Model configurations
│   ├── rag.yaml           # RAG settings
│   ├── api.yaml           # API settings
│   └── config.py          # Config loader
├── src/
│   ├── api/               # FastAPI application
│   │   ├── main.py       # Main app
│   │   └── routes/       # API endpoints
│   ├── models/            # LLM interfaces
│   │   ├── cloud_models.py
│   │   └── local_models.py
│   ├── router/            # Model routing
│   ├── rag/               # RAG system
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retrieval.py
│   ├── citation/          # Citation checker
│   ├── precedent/         # Precedent graph
│   ├── ingestion/         # Data pipeline
│   └── utils/             # Utilities
├── data/                  # Legal data storage
│   ├── state_laws/
│   ├── federal_laws/
│   ├── cases/
│   ├── legal_dictionaries/
│   └── vector_store/
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── SETUP.md
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── requirements.txt       # Dependencies
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Setup Guide](docs/SETUP.md)

## Configuration

### Models

Edit `config/models.yaml` to configure cloud and local models:

```yaml
cloud_models:
  openai:
    enabled: true
    model_name: "gpt-4"
    temperature: 0.3
  anthropic:
    enabled: true
    model_name: "claude-3-opus-20240229"

local_models:
  llama3:
    enabled: true
    model_path: "models/llama3-8b-instruct"
    quantization: "4bit"
```

### RAG

Edit `config/rag.yaml` to configure retrieval settings:

```yaml
embeddings:
  model: "text-embedding-ada-002"
  dimension: 1536

vector_store:
  type: "faiss"
  storage_path: "data/vector_store"

retrieval:
  top_k: 5
  similarity_threshold: 0.7
```

## Requirements

- Python 3.9+
- 16GB+ RAM (for local models)
- GPU with 16GB+ VRAM (recommended for local models)

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions or issues, please open an issue on GitHub.
