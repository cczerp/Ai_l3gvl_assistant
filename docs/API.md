# Legal-AI API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

#### GET /health

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-21T10:00:00",
  "version": "1.0.0"
}
```

### Legal Query

#### POST /api/v1/query

Submit a legal query and get an answer with sources.

**Request:**
```json
{
  "query": "What are the requirements for a valid contract?",
  "jurisdiction": "federal",
  "use_rag": true,
  "prefer_local": false,
  "max_results": 5
}
```

**Response:**
```json
{
  "answer": "A valid contract requires...",
  "sources": [
    {
      "doc_id": "case_12345",
      "score": 0.92,
      "metadata": {
        "citation": "Smith v. Jones, 123 U.S. 456",
        "jurisdiction": "federal"
      },
      "content": "..."
    }
  ],
  "model_used": "gpt-4",
  "confidence": 0.85
}
```

### Citation Checking

#### POST /api/v1/citation/check

Validate legal citations in text.

**Request:**
```json
{
  "text": "As stated in Brown v. Board of Education, 347 U.S. 483..."
}
```

**Response:**
```json
{
  "total_citations": 1,
  "valid_citations": 1,
  "invalid_citations": 0,
  "citations": [
    {
      "text": "347 U.S. 483",
      "type": "case",
      "is_valid": true,
      "errors": []
    }
  ]
}
```

#### POST /api/v1/citation/extract

Extract citations from text.

**Query Parameters:**
- `text` (string): Text to extract citations from

**Response:**
```json
{
  "citations": [
    {
      "text": "347 U.S. 483",
      "type": "case",
      "volume": "347",
      "reporter": "U.S.",
      "page": "483"
    }
  ]
}
```

### Precedent Search

#### POST /api/v1/precedent/search

Search precedent graph for related cases.

**Request:**
```json
{
  "case_id": "case_12345",
  "max_depth": 2,
  "limit": 10
}
```

**Response:**
```json
{
  "related_cases": [
    {
      "case_id": "case_67890",
      "case_name": "Doe v. Roe",
      "citation": "456 F.3d 789",
      "court": "9th Circuit",
      "jurisdiction": "federal"
    }
  ],
  "total_found": 15
}
```

#### GET /api/v1/precedent/citation-count/{case_id}

Get citation statistics for a case.

**Response:**
```json
{
  "cited_by": 127,
  "cites": 45
}
```

### Data Ingestion

#### POST /api/v1/ingest

Ingest legal documents into the system.

**Request:**
```json
{
  "doc_type": "state_laws",
  "state": "CA",
  "start_year": 2020,
  "end_year": 2024
}
```

**Response:**
```json
{
  "status": "completed",
  "statistics": {
    "total_documents": 1234,
    "total_chunks": 5678,
    "errors": 0
  }
}
```

## Rate Limiting

- 60 requests per minute per API key
- Burst size: 10 requests

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
