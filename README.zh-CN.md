# Kwipu（geode_graph 项目）

> 🌐 **语言版本** · [English](README.md) · **简体中文**

一个完全本地运行的 Graph RAG 系统，可以把你的 Markdown 笔记构建成一张可被自然语言查询的知识图谱。用人话提问，就能获得跨多个文件关联出来的答案。

为 [Obsidian](https://obsidian.md/) vault 而生，但同样适用于任何 Markdown 文件夹。

[![Geode Graph 运行截图](https://github.com/benmaster82/Kwipu/raw/main/img/screen.png)](/benmaster82/Kwipu/blob/main/img/screen.png)

[![查询响应示例](https://github.com/benmaster82/Kwipu/raw/main/img/screen_2.png)](/benmaster82/Kwipu/blob/main/img/screen_2.png)

## 核心特性

* **Property Graph 索引** — 使用 LLM 抽取关系，从你的笔记构建知识图谱
* **Obsidian 原生支持** — 自动解析 `[[wikilinks]]` 和 YAML frontmatter，转化为结构化的图三元组
* **多语言** — 支持意大利语、英语、法语、德语、西班牙语、葡萄牙语（自动识别）
* **混合检索** — 同时融合 4 种检索策略：
  + LLM 同义词扩展（可选，`--fast` 模式下跳过）
  + 向量相似度检索
  + BM25 关键词打分
  + 时间/元数据匹配
* **实时同步** — 监听笔记文件夹变化，自动增量更新图索引
* **反幻觉提示词** — 严格要求引用来源，避免编造事实
* **完全本地** — 基于 Ollama 运行，数据绝不离开本机

## 环境要求

* Python 3.11+
* 本地运行的 [Ollama](https://ollama.ai/)
* 一个 LLM 模型（例如 `llama3.1:8b`、`qwen2.5:7b`、`mistral:7b`）
* 一个嵌入模型（默认：`nomic-embed-text`）

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 在 Ollama 中拉取模型
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

在 `geode_graph.py` 中设置你要使用的模型：

```python
MODEL_NAME = "llama3.1:8b"  # 或 Ollama 中任意可用的模型
```

## 使用

```bash
# 完整模式（启用全部检索器，质量最佳）
python geode_graph.py

# 快速模式（跳过 LLM 同义词检索器，CPU 下单次查询快约 50%）
python geode_graph.py --fast
```

把你的 Markdown 文件放到 `./knowledge_base/` 目录下（或者修改配置中的 `KNOWLEDGE_DIR`）。系统首次运行时会构建图，之后持续监听文件变化。

## 工作原理

```
你的笔记 (.md)
      │
      ▼
┌─────────────────────┐
│      预处理         │  ← 提取 [[wikilinks]] 和 YAML frontmatter
│  (lang_config.py)   │  ← 根据上下文推断关系
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     LLM 抽取        │  ← 抽取额外的实体-关系三元组
│  (SimpleLLMPath)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Property Graph     │  ← 合并结构化 + LLM 三元组
│  索引               │  ← 持久化到磁盘 (storage_graph/)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     混合检索        │  ← 同义词 + 向量 + BM25 + 时间维度
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    LLM 生成回答     │  ← 根据召回上下文生成答案
└─────────────────────┘
```

## 项目结构

```
├── geode_graph.py       # 主程序入口
├── lang_config.py       # 多语言配置（停用词、模式、关系）
├── requirements.txt     # Python 依赖
├── knowledge_base/      # 把你的笔记放在这里
│   └── examples/        # 示例笔记，方便上手
└── storage_graph/       # 自动生成的图索引（已在 .gitignore 中）
```

## 指向 Obsidian Vault

把 `KNOWLEDGE_DIR` 改为你的 vault 路径：

```python
KNOWLEDGE_DIR = "C:/Users/YourName/Documents/MyVault"
```

系统只读取文件，不会修改任何内容。`.obsidian/` 配置目录会被自动忽略。

## 模型推荐

| 模型规模 | 内存（Q4） | 质量 | CPU 速度 | GPU 速度 |
| --- | --- | --- | --- | --- |
| 1B | ~2 GB | 基础可用 | ~8s | ~2s |
| 3B | ~3 GB | 良好 | ~60s | ~8s |
| 7-8B | ~5-6 GB | 优秀 | ~300s | ~15-25s |
| 20B | ~12 GB | 最佳 | 不推荐 | ~15s |

正式使用推荐 7B+ 配合 GPU，体验最为均衡。

## 构建时间预估

首次构建图时，每个文档分块都需要一次 LLM 调用。之后从磁盘加载图，速度是秒级的。

| 笔记数量 | GPU (7B) | CPU (7B) | CPU (3B) |
| --- | --- | --- | --- |
| 5 | ~2 分钟 | ~5 分钟 | ~3 分钟 |
| 20 | ~7 分钟 | ~20 分钟 | ~10 分钟 |
| 50 | ~17 分钟 | ~50 分钟 | ~25 分钟 |
| 100 | ~35 分钟 | ~100 分钟 | ~50 分钟 |
| 500+ | ~3 小时 | 不推荐 | ~4 小时 |

新增一个文件采用增量更新（约 20-60 秒），**不会重建整个图**。

## 资源占用

| 组件 | 内存 | 备注 |
| --- | --- | --- |
| Ollama（LLM） | 2-14 GB | 取决于模型规模和量化等级 |
| Ollama（嵌入） | ~300 MB | nomic-embed-text |
| Geode Graph（建图） | 0.5-4 GB | 取决于笔记数量 |
| Geode Graph（查询） | 200-500 MB | 图构建完成后 |
| **合计（7B Q4）** | **~8-12 GB** | **建议最低系统内存：16 GB** |

## 实用技巧：用云端模型建图，本地模型日常查询

如果你的硬件比较有限，可以通过 Ollama 接入一次性的强力云端模型来构建图，然后切换为轻量级本地模型做日常查询。图持久化在磁盘上，因此只有构建阶段才需要大模型。

```bash
# 步骤 1：用云端模型构建图（一次性，高质量抽取）
# 在 geode_graph.py 中设置 MODEL_NAME = "gpt-oss:20b-cloud"，然后运行：
python geode_graph.py
# 等待出现 "Graph built and saved successfully"，然后退出。

# 步骤 2：切换为小模型用于查询（快速，低资源占用）
# 在 geode_graph.py 中设置 MODEL_NAME = "qwen2.5:3b"，然后运行：
python geode_graph.py --fast
```

这样可以兼顾两端的优势：由 20B+ 模型构建出高质量的图，再由 3B 模型实现快速轻量的查询。图结构（实体、关系、三元组）与模型解耦，**切换模型不会影响图本身，只影响回答生成质量**。

## 路线图

* **Telegram Bot** — 通过 Telegram 随时随地查询你的 Obsidian vault 或知识库，外出时也能基于自己的笔记问答。

## 媒体报道

* [《把 Markdown 笔记变成可问答的知识图谱：本地 Graph RAG 工具 Kwipu 实测》](https://juejin.cn/post/7637134822670876699) — 掘金 · 龙哥AI · 2026-05-08

## 许可协议

MIT
