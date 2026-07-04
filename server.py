#!/usr/bin/env python3
"""AutoPoC HTTP Wrapper for Kwipu Graph RAG.

Exposes health, status, and query endpoints as HTTP API
to validate containerized deployment on OpenShift.
"""
import http.server
import json
import os
import sys
import threading
import time
import traceback
import urllib.request

PORT = int(os.environ.get("PORT", "8080"))
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
KNOWLEDGE_DIR = os.environ.get("KNOWLEDGE_DIR", "./knowledge_base/examples")

# Global state
graph_rag = None
graph_ready = False
init_error = None


def init_graph():
    """Initialize the Graph RAG engine in a background thread."""
    global graph_rag, graph_ready, init_error
    try:
        print(f"Waiting for Ollama at {OLLAMA_BASE_URL}...", flush=True)
        for attempt in range(30):
            try:
                req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp.read()
                print("Ollama is ready.", flush=True)
                break
            except Exception:
                time.sleep(5)
                if attempt == 29:
                    init_error = "Ollama not reachable after 150 seconds"
                    print(f"ERROR: {init_error}", flush=True)
                    return

        # Import and initialize
        from geode_graph import WritHerGraphRAG, _init_llm
        
        model_name = os.environ.get("LLM_MODEL", "qwen2.5:1.5b")
        embed_model = os.environ.get("EMBED_MODEL", "nomic-embed-text")
        
        print(f"Initializing LLM: {model_name}, Embeddings: {embed_model}", flush=True)
        _init_llm(model_name=model_name, embed_model=embed_model)
        
        print(f"Building graph from {KNOWLEDGE_DIR}...", flush=True)
        graph_rag = WritHerGraphRAG(knowledge_dir=KNOWLEDGE_DIR)
        graph_rag.load_or_build_index()
        
        graph_ready = True
        print("Graph RAG initialized successfully.", flush=True)
    except Exception as e:
        init_error = f"{type(e).__name__}: {e}"
        print(f"ERROR initializing graph: {init_error}", flush=True)
        traceback.print_exc()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default access logs

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path in ("/health", "/healthz"):
            self._send_json(200, {
                "status": "ok",
                "service": "kwipu-poc",
                "graph_ready": graph_ready,
                "init_error": init_error,
            })
        elif self.path == "/status":
            status_data = {
                "service": "kwipu-poc",
                "graph_ready": graph_ready,
                "init_error": init_error,
                "knowledge_dir": KNOWLEDGE_DIR,
                "ollama_url": OLLAMA_BASE_URL,
            }
            if graph_ready and graph_rag:
                try:
                    status_data["graph_nodes"] = "available"
                except Exception:
                    pass
            self._send_json(200, status_data)
        elif self.path == "/":
            self._send_json(200, {
                "service": "kwipu-poc",
                "description": "Kwipu Graph RAG - AutoPoC HTTP Wrapper",
                "endpoints": ["/health", "/status", "/query"],
            })
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/query":
            if not graph_ready:
                self._send_json(503, {
                    "error": "Graph not ready",
                    "init_error": init_error,
                })
                return
            
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                data = json.loads(body)
                question = data.get("question", "")
                if not question:
                    self._send_json(400, {"error": "Missing 'question' field"})
                    return
                
                print(f"Query: {question}", flush=True)
                answer = graph_rag.ask(question)
                self._send_json(200, {
                    "question": question,
                    "answer": str(answer),
                    "service": "kwipu-poc",
                })
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    # Start graph initialization in background
    init_thread = threading.Thread(target=init_graph, daemon=True)
    init_thread.start()

    # Start HTTP server immediately (health endpoint works before graph is ready)
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Kwipu AutoPoC server listening on port {PORT}", flush=True)
    print(f"Health: http://localhost:{PORT}/health", flush=True)
    server.serve_forever()
