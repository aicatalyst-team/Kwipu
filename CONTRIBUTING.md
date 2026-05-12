# Contributing to Kwipu

Thanks for your interest in contributing. This guide will help you get started.

## Getting Started

```bash
git clone https://github.com/benmaster82/Kwipu.git
cd Kwipu
pip install -r requirements.txt
```

Make sure you have [Ollama](https://ollama.ai/) installed and running with at least one model:

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

## Project Overview

Kwipu is a local Graph RAG system. The codebase is intentionally small:

- `geode_graph.py` - Main application (engine, retrievers, CLI, file watcher)
- `lang_config.py` - Multilingual support (stopwords, relation patterns, date extraction)
- `knowledge_base/examples/` - Sample notes for testing

## How to Contribute

1. **Open an issue first** if you want to discuss an approach before writing code.
2. **Fork the repo** and create a branch from `main`.
3. **One feature per PR.** Small, focused PRs get reviewed faster.
4. **Test with real notes.** If possible, test with an actual Obsidian vault or a set of interconnected markdown files.
5. **Write in English.** Code, comments, commit messages, and documentation should all be in English.

## Areas Where Help is Needed

### Retriever Attribution Logging
Log which retriever (vector, BM25, temporal, synonym) contributed context for each answer. This helps users understand why the system gave a specific response and makes tuning easier.

### Evaluation Set
Build a categorized test suite with question-answer pairs:
- Exact-source questions (answer must cite a specific note)
- Graph traversal questions (requires 2+ edges)
- Temporal questions (depends on dates)
- Negative questions (vault doesn't have the answer)

### Provenance Inspector
Surface the chain: answer claim -> cited note -> heading/block -> extracted entity/edge. This lets users correct bad triples without the system being a black box.

### Telegram Bot
Query the knowledge base remotely via Telegram. Should work as a separate module that imports the engine.

### Incremental Updates on Modification
Currently, modifying a file triggers a full graph rebuild. Implementing delete-then-reinsert for modified files would make the system much faster on large vaults.

## Code Style

- Keep it simple. This is a local-first tool, not an enterprise platform.
- No unnecessary abstractions. If a function is only used once, it probably doesn't need to be extracted.
- Comments should explain "why", not "what".
- Use type hints on function signatures.

## Commit Messages

Use short, descriptive commit messages:

```
Add retriever attribution logging
Fix BOM handling in frontmatter parser
Update build time estimates in README
```

## Running the Project

```bash
# Standard mode
python geode_graph.py

# Fast mode (no synonym retriever)
python geode_graph.py --fast

# With model override
python geode_graph.py --llm-model qwen2.5:7b
```

## Questions?

Open an issue or start a discussion on the repo. We're happy to help.
