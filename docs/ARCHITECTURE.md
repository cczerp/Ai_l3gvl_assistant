# Legal-AI Assistant Architecture

## Overview

The Legal-AI Assistant is a hybrid legal AI system that combines cloud models (GPT-4, Claude) with local models (Llama3, Mixtral) to provide comprehensive legal question answering with RAG capabilities.

## System Components

### 1. Model Layer

#### Cloud Models
- **OpenAI GPT-4**: For complex legal reasoning and analysis
- **Anthropic Claude**: For legal research and document drafting

#### Local Models
- **Llama3 8B**: For quick queries and citation extraction
- **Mixtral 8x7B**: For legal summarization and precedent matching

### 2. Router

The intelligent router selects the appropriate model based on:
- Query complexity
- Cost optimization
- Performance requirements
- Availability and fallback strategies

**Routing Strategies:**
- `cost_optimized`: Prefer local models when possible
- `performance`: Always use best available model
- `hybrid`: Balance cost and performance

### 3. RAG System

#### Embeddings
- Cloud: OpenAI text-embedding-ada-002
- Local: sentence-transformers/all-MiniLM-L6-v2
- Dimension: 1536 (configurable)

#### Vector Store
- Primary: FAISS (local, fast)
- Alternative: Pinecone, Weaviate, ChromaDB
- Features: Metadata filtering, hybrid search

#### Retrieval
- Top-K similarity search
- Reranking with cross-encoder
- Context window management
- Jurisdiction-based filtering

### 4. Data Sources

#### State Laws (50 States)
- Path: `data/state_laws/{state}/`
- Metadata: state, statute_number, effective_date
- Chunk size: 1000 characters

#### Federal Laws
- Path: `data/federal_laws/`
- Metadata: USC title, section, agency
- Chunk size: 1000 characters

#### Case Law (50 Years)
- Path: `data/cases/`
- Metadata: citation, court, date, jurisdiction
- Chunk size: 1500 characters
- Coverage: 1974-2024

#### Legal Dictionaries
- Path: `data/legal_dictionaries/`
- Metadata: term, source, jurisdiction
- Chunk size: 500 characters

### 5. Citation Checker

Features:
- Citation extraction (multiple formats)
- Citation validation
- Parallel citation finding
- Format conversion (Bluebook, ALWD)
- Shepard's citator integration (stub)

### 6. Precedent Graph

Graph database for case relationships:
- Case nodes with metadata
- Citation edges (followed, distinguished, overruled)
- Precedent chain analysis
- Citation count statistics
- Topic-based search

### 7. Ingestion Pipeline

Document processing pipeline:
- Document type detection
- Metadata extraction
- Text chunking with overlap
- Embedding generation
- Vector store indexing

### 8. API Layer

RESTful API with FastAPI:
- `/api/v1/query` - Legal question answering
- `/api/v1/citation/check` - Citation validation
- `/api/v1/precedent/search` - Precedent graph search
- `/api/v1/ingest` - Document ingestion
- `/health` - Health check

## Data Flow

```
User Query → Router → Model Selection
              ↓
         RAG Retrieval
              ↓
    [State Laws, Federal Laws, Cases, Dictionaries]
              ↓
         Vector Store
              ↓
      Embedding Match
              ↓
    Context + Query → Model → Answer
              ↓
      Citation Check → Precedent Graph
              ↓
         Response
```

## Configuration

All configuration is managed through YAML files:
- `config/models.yaml` - Model configurations
- `config/rag.yaml` - RAG and vector store settings
- `config/api.yaml` - API server settings

## Security

- JWT authentication
- API key management via environment variables
- Rate limiting
- CORS configuration
- Input validation

## Scalability

- Horizontal scaling with multiple workers
- Vector store sharding
- Caching layer (planned)
- Async processing for ingestion
- Load balancing between models

## Future Enhancements

- Real-time case law updates
- Multi-modal support (PDF, images)
- Fine-tuned legal models
- Advanced precedent analytics
- Collaborative features
