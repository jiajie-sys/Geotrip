# 🌍 GeoTrip

> An AI-powered outdoor travel planning assistant with RAG, structured destination data, weather awareness, and dynamic itinerary replanning.

GeoTrip 是一个基于大语言模型的 AI 户外旅行规划助手。

用户输入目的地、出发日期、旅行天数、预算、交通方式和旅行偏好后，GeoTrip 会结合旅行知识库、结构化景点数据、天气信息和大语言模型生成个性化行程，并在天气风险发生变化时自动评估风险并重新规划行程。

与单纯依赖 Prompt 生成旅行计划不同，GeoTrip 尝试构建一个完整的：

**LLM Planning → External Information → Risk Evaluation → Dynamic Replanning**

闭环。

---

## ✨ Features

### 🤖 AI Travel Planning

根据用户提供的：

- 目的地
- 出发日期
- 旅行天数
- 预算
- 交通方式
- 兴趣偏好

GeoTrip 自动生成结构化的逐日旅行计划。

生成结果经过 Pydantic 数据模型验证，以保证输出结构能够被后端、数据库和前端稳定使用。

---

### 📚 RAG Knowledge Retrieval

GeoTrip 使用 RAG（Retrieval-Augmented Generation）增强旅行规划。

知识库文本经过：

```text
Travel Knowledge
      ↓
Text Chunking
      ↓
Sentence Transformer
      ↓
Embedding
      ↓
FAISS Vector Index
      ↓
Top-K Retrieval
      ↓
LLM Context
```

系统使用向量检索获取与目的地、季节和旅行需求相关的知识，并将检索结果作为上下文提供给 LLM。

这能够减少完全依赖模型内部知识造成的幻觉，同时允许系统接入自定义旅行知识。

---

### 📍 Structured Places Retrieval

除了非结构化 RAG 知识库之外，GeoTrip 还维护了一套轻量级结构化景点数据。

景点数据存储在：

```text
data/places/attractions.json
```

每个景点可以包含：

- attraction name
- country
- city
- attraction type
- tags
- recommended duration

系统通过 Places Tool 根据目的地搜索相关景点，并将结果加入旅行规划上下文。

因此 GeoTrip 的旅行规划信息来源不再只有 LLM 和向量知识库，而是同时结合：

```text
Unstructured Knowledge
        +
Structured Places Data
        +
Weather Information
        ↓
Planning Context
        ↓
DeepSeek LLM
```

---

### 🌦 Weather-aware Planning

GeoTrip 接入天气服务获取旅行日期附近的天气信息。

当旅行日期位于可用天气预报范围内时，系统会将：

- 降水概率
- 风速
- 最低温度
- 最高温度

等天气信息加入旅行规划上下文。

LLM 可以据此生成更符合实际环境的旅行计划。

---

### ⚠️ Weather Risk Evaluation

系统不会直接让 LLM 决定是否需要重新规划。

GeoTrip 首先通过确定性的风险规则对天气进行评估：

```text
Weather Data
     ↓
Risk Evaluation
     ↓
Low / Medium / High
     ↓
Need Replanning?
```

只有达到高风险条件时，系统才会触发重新规划。

这种设计将：

**确定性规则判断**

与

**LLM 生成能力**

进行组合，使系统行为更加稳定和可解释。

---

### 🔄 Dynamic Replanning

当检测到高风险天气时，GeoTrip 会：

```text
Original Plan V1
       ↓
Weather Risk Detection
       ↓
Retrieve Relevant Knowledge
       ↓
LLM Replanning
       ↓
Updated Plan V2
```

重新规划后的行程会保存为新的版本，而不会覆盖原始行程。

这样系统不仅能够生成旅行计划，还能够根据外部环境变化动态调整计划。

---

### 🕓 Trip Version History

GeoTrip 支持保存旅行计划版本。

例如：

```text
Version 1
Original AI-generated itinerary

        ↓ Weather changes

Version 2
Weather-aware replanned itinerary
```

系统可以查询不同版本，并比较两个版本之间的变化。

---

### 🔍 Version Comparison

系统可以自动分析两个旅行计划版本中的：

- 保留活动
- 删除活动
- 新增活动
- 修改天数

从而直观展示重新规划前后的差异。

---

### 🖥 Streamlit Frontend

GeoTrip 提供 Streamlit Web 界面。

用户可以直接在浏览器中：

1. 输入旅行需求
2. 生成 AI 行程
3. 查看旅行计划
4. 模拟天气变化
5. 触发动态重新规划
6. 查看 V1 / V2 行程
7. 比较不同版本

---

## 🏗 Architecture

```text
                     ┌──────────────────────┐
                     │      Streamlit       │
                     │       Frontend       │
                     └──────────┬───────────┘
                                │ HTTP
                                ▼
                     ┌──────────────────────┐
                     │       FastAPI        │
                     │       Backend        │
                     └──────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
 ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
 │     RAG     │         │   Places    │         │   Weather   │
 │  Retrieval  │         │    Tool     │         │    Tool     │
 └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
        │                       │                       │
        ▼                       ▼                       ▼
 ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
 │    FAISS    │         │ Attractions │         │Weather Risk │
 │Vector Store │         │    JSON     │         │ Evaluation  │
 └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ DeepSeek LLM│
                         │  Planning   │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │   SQLite    │
                         │  Database   │
                         └─────────────┘
```

---

## 🧠 Core Workflow

GeoTrip 的核心流程：

```text
User Travel Request
        ↓
FastAPI Backend
        ↓
┌───────────────────────────────┐
│                               │
▼                               ▼
RAG Retrieval              Places Retrieval
│                               │
└──────────────┬────────────────┘
               ↓
        Weather Retrieval
               ↓
        Prompt Construction
               ↓
          DeepSeek LLM
               ↓
      Structured Trip Plan
               ↓
      Pydantic Validation
               ↓
       SQLite Persistence
               ↓
   Weather Risk Evaluation
               ↓
           High Risk?
        ┌──────┴──────┐
        │             │
       No            Yes
        │             ↓
   Keep Plan      RAG Retrieval
                      ↓
                LLM Replanning
                      ↓
                Trip Version V2
                      ↓
               Version Comparison
```

GeoTrip 的核心设计思路可以概括为：

```text
Retrieve
   ↓
Plan
   ↓
Validate
   ↓
Persist
   ↓
Evaluate
   ↓
Replan
```

---

## 🛠 Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| LLM | DeepSeek |
| RAG | Sentence Transformers |
| Vector Database | FAISS |
| Structured Data | JSON |
| Database | SQLite |
| Validation | Pydantic |
| Weather | Open-Meteo |
| HTTP Client | Requests |
| Testing | Pytest |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |

---

## 📁 Project Structure

```text
GeoTrip/
│
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── prompts.py
│   │
│   ├── services/
│   │   ├── planner.py
│   │   ├── replanner.py
│   │   └── version_compare.py
│   │
│   ├── rag/
│   │   ├── knowledge_loader.py
│   │   ├── retriever.py
│   │   └── faiss_store.py
│   │
│   └── tools/
│       ├── places.py
│       ├── weather.py
│       └── weather_risk.py
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── knowledge/
│   │   ├── iceland.md
│   │   ├── japan.md
│   │   ├── norway.md
│   │   └── universal_travel.md
│   │
│   └── places/
│       └── attractions.json
│
├── scripts/
│   ├── build_index.py
│   └── test_rag.py
│
├── tests/
│   ├── test_weather_risk.py
│   └── test_version_compare.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── README.md
```

---

## 📚 Knowledge Base & Retrieval

GeoTrip combines unstructured travel knowledge with structured destination data to provide richer context for itinerary generation.

### Travel Knowledge Base

Destination-specific travel knowledge is stored as Markdown documents under:

```text
data/knowledge/
├── iceland.md
├── japan.md
├── norway.md
└── universal_travel.md
```

The knowledge base contains information such as:

- seasonal travel conditions
- outdoor activities
- transportation
- equipment recommendations
- weather considerations
- safety advice
- general travel guidelines

During index construction, the documents are split into chunks and converted into vector embeddings using Sentence Transformers.

The embeddings are stored in a FAISS vector index and retrieved using semantic similarity.

```text
Travel Documents
      ↓
Knowledge Loader
      ↓
Text Chunking
      ↓
Sentence Transformer
      ↓
Vector Embeddings
      ↓
FAISS Index
      ↓
Top-K Retrieval
      ↓
LLM Planning Context
```

This design allows the travel knowledge base to be updated independently from the LLM.

New destination knowledge can be added by extending the Markdown documents and rebuilding the vector index.

---

### Structured Places Data

GeoTrip also contains a lightweight structured attraction dataset:

```text
data/places/attractions.json
```

The Places Tool searches destination-specific attractions and provides structured information such as:

```text
Attraction Name
Country
City
Type
Tags
Recommended Days
```

Example conceptual record:

```json
{
  "name": "Golden Circle",
  "country": "Iceland",
  "city": "Reykjavik",
  "type": "road trip",
  "tags": [
    "waterfall",
    "geothermal",
    "nature"
  ],
  "recommended_days": 1
}
```

Structured attraction information is combined with RAG context before itinerary generation.

This creates two complementary retrieval paths:

```text
                  User Request
                       ↓
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
  Semantic Retrieval       Structured Retrieval
          │                         │
          ▼                         ▼
   FAISS Knowledge             Places Tool
          │                         │
          └────────────┬────────────┘
                       ↓
                 Prompt Context
                       ↓
                  DeepSeek LLM
                       ↓
              Structured Itinerary
```

RAG is better suited for retrieving descriptive travel knowledge, while structured Places data provides explicit destination entities and attributes.

---

### Retrieval Verification

A lightweight retrieval test script is provided:

```bash
python -m scripts.test_rag
```

It can be used to inspect retrieved knowledge chunks and verify whether the FAISS index returns destination-relevant context.

The retrieval pipeline has been manually tested using destination and seasonal travel queries.

For example, queries about Iceland can retrieve relevant information concerning:

- seasonal conditions
- October travel
- equipment recommendations
- outdoor safety
- weather conditions

This provides a simple way to inspect retrieval quality while developing the knowledge base.

---

## 🔨 Building the RAG Index

When travel knowledge is modified, the FAISS index can be rebuilt with:

```bash
python -m scripts.build_index
```

The process is:

```text
Markdown Knowledge
        ↓
Load Documents
        ↓
Chunk Documents
        ↓
Generate Embeddings
        ↓
Normalize Embeddings
        ↓
Build FAISS Index
        ↓
Persist Index
```

After rebuilding the index, retrieval can be verified using:

```bash
python -m scripts.test_rag
```

---

## 🚀 Running with Docker

### 1. Clone the repository

```bash
git clone https://github.com/jiajie-sys/Geotrip.git
cd Geotrip
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

> `.env` is excluded from Git and should never be committed to the repository.

### 3. Build containers

```bash
docker compose build
```

The Docker image uses CPU-based PyTorch for embedding inference, so a CUDA-capable GPU is not required to run GeoTrip.

### 4. Start GeoTrip

```bash
docker compose up
```

The first startup may take additional time while the Sentence Transformer model is downloaded and initialized.

After startup:

Frontend:

```text
http://localhost:8501
```

FastAPI Swagger:

```text
http://localhost:8000/docs
```

### 5. Stop GeoTrip

Press:

```text
Ctrl + C
```

or run:

```bash
docker compose down
```

---

## 💻 Running Locally

GeoTrip can also be run without Docker.

### Start Backend

```bash
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Start Frontend

Open another terminal and run:

```bash
streamlit run frontend/app.py
```

Frontend:

```text
http://localhost:8501
```

---

## 🧪 Testing

Run unit tests:

```bash
pytest
```

Current tests cover core deterministic components including:

```text
Weather Risk Evaluation
Version Comparison
```

The current test suite verifies multiple risk levels and itinerary comparison behavior.

RAG retrieval can additionally be inspected with:

```bash
python -m scripts.test_rag
```

---

## 🔌 API

GeoTrip exposes REST APIs through FastAPI.

Main endpoints include:

```text
POST   /api/v1/trips/plan

GET    /api/v1/trips/{trip_id}

PATCH  /api/v1/trips/{trip_id}/budget

DELETE /api/v1/trips/{trip_id}

POST   /api/v1/trips/{trip_id}/replan

GET    /api/v1/trips/{trip_id}/versions

GET    /api/v1/trips/{trip_id}/versions/{version}

GET    /api/v1/trips/{trip_id}/versions/compare
```

Interactive API documentation is available through Swagger:

```text
http://localhost:8000/docs
```

---

## 💡 Design Decisions

### Why RAG instead of pure prompting?

Pure LLM generation depends heavily on model knowledge and may produce inaccurate or generic destination-specific information.

GeoTrip retrieves relevant travel knowledge before generation and injects it into the planning context.

This allows the system to use an independently maintained travel knowledge base rather than relying entirely on the model's internal knowledge.

---

### Why combine RAG with structured Places data?

Vector retrieval is suitable for semantic knowledge such as:

```text
seasonal conditions
travel advice
equipment recommendations
safety information
```

However, attractions are naturally structured entities.

For example:

```text
name
country
city
type
tags
recommended duration
```

GeoTrip therefore separates these two information sources:

```text
Travel Knowledge → RAG / FAISS

Attraction Data → Structured Places Tool
```

Both are then combined during prompt construction.

This keeps the system simple while allowing different information types to use appropriate retrieval methods.

---

### Why not let the LLM decide weather risk?

Risk evaluation should be predictable.

GeoTrip therefore uses deterministic rules to decide whether replanning is required and uses the LLM only for generating the new itinerary.

This separates:

```text
Decision Logic → Deterministic Program

Content Generation → LLM
```

The LLM does not independently decide whether a high-risk weather condition should trigger replanning.

---

### Why store itinerary versions?

Dynamic travel planning should preserve history.

Instead of replacing the original itinerary, GeoTrip stores replanned itineraries as new versions.

For example:

```text
V1
Original itinerary
       ↓
Weather changes
       ↓
Risk evaluation
       ↓
V2
Replanned itinerary
```

This makes changes traceable and allows the frontend or API to compare different planning results.

---

### Why validate LLM output?

LLM output is probabilistic and may occasionally contain malformed JSON or unexpected structures.

GeoTrip therefore validates generated plans using Pydantic before accepting them.

Conceptually:

```text
LLM Response
     ↓
JSON Parsing
     ↓
Pydantic Validation
     ↓
Day Count Validation
     ↓
Valid?
 ┌───┴───┐
 │       │
Yes      No
 │       │
Save    Retry
```

This provides a reliability layer between probabilistic LLM generation and deterministic application logic.

---

## ⚠️ Current Limitations

GeoTrip is currently a prototype and still has several limitations:

- The travel knowledge base currently covers a limited number of destinations and is intended as a prototype dataset rather than a production-scale travel database.
- Structured attraction data currently contains only a small number of representative destinations and attractions.
- RAG retrieval quality depends on knowledge chunking and embedding quality.
- Retrieval evaluation is currently lightweight and primarily based on manual inspection.
- Weather risk thresholds are prototype rules rather than official travel-safety standards.
- Version comparison currently relies primarily on normalized activity text matching.
- Semantically similar but differently worded activities may therefore be classified as removed and added.
- Weather forecasts are only available within the supported forecast window.
- The current system focuses on itinerary planning rather than real-time booking.
- External data sources may occasionally be unavailable or rate-limited.
- GeoTrip has not yet been deployed as a production-scale public service.

These limitations provide clear directions for future engineering improvements.

---

## 🔮 Future Improvements

Potential improvements include:

- Expand destination coverage and structured attraction data
- Build a larger retrieval evaluation dataset
- Add retrieval metrics
- Improve RAG chunking and ranking
- Add reranking for retrieved knowledge
- Improve semantic itinerary comparison using embeddings
- Add map visualization
- Add hotel and transportation data sources
- Add stronger exception handling and observability
- Cache external API and embedding results
- Improve model and vector index caching in Docker
- Deploy GeoTrip as a public web service

These improvements are intentionally kept outside the current V1.0 scope so that the project remains focused on demonstrating a complete AI application engineering workflow.

---

## 🎯 What GeoTrip Demonstrates

GeoTrip is designed primarily as an AI application engineering project.

The project demonstrates how multiple AI and traditional software components can be combined into one complete system:

```text
LLM Application Development
          +
RAG
          +
Vector Retrieval
          +
Structured Tool Data
          +
External API Integration
          +
Deterministic Decision Logic
          +
Dynamic Replanning
          +
Data Persistence
          +
Version Management
          +
REST API
          +
Web Frontend
          +
Testing
          +
Containerization
```

Rather than treating the LLM as the entire application, GeoTrip uses the LLM as one component inside a larger deterministic software system.

---

## 📌 Project Status

**GeoTrip V1.0 — Core workflow completed**

Implemented:

```text
AI Trip Planning
        +
RAG Retrieval
        +
FAISS Vector Search
        +
Structured Places Retrieval
        +
Weather Integration
        +
Risk Evaluation
        +
Dynamic Replanning
        +
Version Management
        +
Version Comparison
        +
SQLite Persistence
        +
Pydantic Validation
        +
Streamlit UI
        +
FastAPI REST API
        +
Unit Tests
        +
Docker Deployment
```

The complete core workflow has been tested end-to-end:

```text
User Request
     ↓
Knowledge / Places Retrieval
     ↓
AI Planning
     ↓
Structured Validation
     ↓
Database Persistence
     ↓
Weather Risk Simulation
     ↓
Dynamic Replanning
     ↓
Version V2
     ↓
Version Comparison
```

GeoTrip V1.0 is currently being prepared as a portfolio project for AI application development.

---

## 📄 License

This project is currently intended for learning, experimentation, and portfolio demonstration purposes.