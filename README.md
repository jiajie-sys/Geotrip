# 🌍 GeoTrip

> An AI-powered outdoor travel planning assistant with RAG, real-time weather awareness, and dynamic itinerary replanning.

GeoTrip 是一个基于大语言模型的 AI 户外旅行规划助手。

用户输入目的地、出发日期、旅行天数、预算、交通方式和旅行偏好后，GeoTrip 会结合旅行知识库、天气信息和大语言模型生成个性化行程，并在天气风险发生变化时自动评估风险并重新规划行程。

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

自动生成结构化的逐日旅行计划。

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

系统使用向量检索获取与目的地和旅行需求相关的知识，并将检索结果作为上下文提供给 LLM。

这能够减少完全依赖模型内部知识造成的幻觉，并允许系统接入自定义旅行知识。

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
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
      ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
      │     RAG     │    │   Weather   │    │   SQLite    │
      │  Retrieval  │    │    Tool     │    │  Database   │
      └──────┬──────┘    └──────┬──────┘    └─────────────┘
             │                  │
             ▼                  ▼
      ┌─────────────┐    ┌─────────────┐
      │    FAISS    │    │ Weather Risk│
      │Vector Store │    │ Evaluation  │
      └──────┬──────┘    └──────┬──────┘
             │                  │
             └──────────┬───────┘
                        ▼
                 ┌─────────────┐
                 │ DeepSeek LLM│
                 │  Planning   │
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
RAG Retrieval
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
    ┌───────┴───────┐
    │               │
   No              Yes
    │               ↓
 Keep Plan     RAG Retrieval
                    ↓
               LLM Replanning
                    ↓
               Trip Version V2
                    ↓
              Version Comparison
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
│       ├── weather.py
│       └── weather_risk.py
│
├── frontend/
│   └── app.py
│
├── data/
│   └── knowledge/
│
├── scripts/
│   └── build_index.py
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

### 4. Start GeoTrip

```bash
docker compose up
```

After startup:

Frontend:

```text
http://localhost:8501
```

FastAPI Swagger:

```text
http://localhost:8000/docs
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

Pure LLM generation depends heavily on model knowledge and may produce inaccurate destination-specific information.

GeoTrip retrieves relevant travel knowledge before generation and injects it into the planning context.

---

### Why not let the LLM decide weather risk?

Risk evaluation should be predictable.

GeoTrip therefore uses deterministic rules to decide whether replanning is required and uses the LLM only for generating the new itinerary.

This separates:

```text
Decision Logic → deterministic program

Content Generation → LLM
```

---

### Why store itinerary versions?

Dynamic travel planning should preserve history.

Instead of replacing the original itinerary, GeoTrip stores replanned itineraries as new versions, making changes traceable and comparable.

---

## ⚠️ Current Limitations

GeoTrip is currently a prototype and still has several limitations:

- The travel knowledge base is currently limited in scale.
- RAG retrieval quality depends on knowledge chunking and embedding quality.
- Weather risk thresholds are prototype rules rather than official travel-safety standards.
- Version comparison currently relies primarily on normalized activity text matching.
- Weather forecasts are only available within the supported forecast window.
- The current system focuses on itinerary planning rather than real-time booking.

These limitations provide clear directions for future engineering improvements.

---

## 🔮 Future Improvements

Potential improvements include:

- Expand destination knowledge base
- Improve semantic itinerary comparison
- Add retrieval evaluation
- Improve RAG chunking and ranking
- Add map visualization
- Add hotel / transportation data sources
- Add stronger exception handling and observability
- Deploy GeoTrip as a public web service

---

## 📌 Project Status

**GeoTrip V1.0 — Core workflow completed**

Implemented:

```text
AI Trip Planning
        +
RAG Retrieval
        +
Weather Integration
        +
Risk Evaluation
        +
Dynamic Replanning
        +
Version Management
        +
Streamlit UI
        +
FastAPI REST API
        +
Unit Tests
        +
Docker Deployment
```

The project is currently being prepared as a portfolio project for AI application development.