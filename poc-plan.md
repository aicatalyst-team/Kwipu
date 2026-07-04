# PoC Plan: Kwipu (Graph RAG over Markdown)

## Project Classification
- **Type:** rag
- **Key Technologies:** Python, LlamaIndex, Ollama, Graph RAG, BM25, Vector Search
- **ODH Relevance:** Validates deployment of a Graph RAG pipeline on OpenShift with local LLM inference via Ollama sidecar, demonstrating multi-container AI workloads.

## PoC Objectives
1. Containerize the Kwipu Python application with UBI base image
2. Deploy with an Ollama sidecar for local LLM inference
3. Expose a REST API via a thin HTTP wrapper for graph queries
4. Validate the pipeline can ingest Markdown files and answer questions

## Infrastructure Requirements
- **Resource Profile:** medium (1Gi RAM, 500m CPU for Kwipu; Ollama needs more)
- **GPU Required:** No (CPU inference with small models)
- **Persistent Storage:** None for PoC (example data bundled in image)
- **Sidecar Containers:** Ollama (for LLM and embeddings)
- **Deployment Model:** deployment
- **Listens on Port:** true (via HTTP wrapper on port 8080)
- **LLM API Required:** No (uses local Ollama)

## Test Scenarios

### Scenario 1: Health Check
- **Description:** Verify the HTTP health endpoint returns 200 OK
- **Type:** http
- **Input:** GET /health
- **Expected:** HTTP 200 with JSON status
- **Timeout:** 30s

### Scenario 2: Graph Query
- **Description:** Query the knowledge base about example data
- **Type:** http
- **Input:** POST /query with {"question": "What is Project Alpha?"}
- **Expected:** HTTP 200 with response containing answer text
- **Timeout:** 120s (LLM inference takes time on CPU)

### Scenario 3: Index Status
- **Description:** Check if the knowledge graph has been built
- **Type:** http
- **Input:** GET /status
- **Expected:** HTTP 200 with index statistics
- **Timeout:** 30s

## Dockerfile Considerations
- Use UBI9 Python 3.12 image
- Install llama-index and dependencies from requirements.txt
- Create a thin HTTP wrapper (server.py) using only stdlib
- Bundle the example knowledge_base directory
- Make Ollama URL configurable via OLLAMA_BASE_URL env var

## Deployment Considerations
- Deploy Kwipu as main container with HTTP wrapper on port 8080
- Deploy Ollama as a sidecar container in the same pod
- Use small models (qwen2.5:1.5b for LLM, nomic-embed-text for embeddings)
- Init container to pull Ollama models before app starts
