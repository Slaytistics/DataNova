<div align="center">

# 🚀 DataNova AI

### No-Code Intelligent Data Analysis & Visualization Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![GPT-4](https://img.shields.io/badge/GPT--4-Powered-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

**DataNova bridges the gap between raw data and actionable insight — no data science background required.**

[Live Demo](https://datanova-frontend.vercel.app/) · [Report Bug](https://github.com/Slaytistics/DataNova/issues) · [Request Feature](https://github.com/Slaytistics/DataNova/issues)

</div>

---

## 🧠 Overview

DataNova is a full-stack, AI-powered web application that transforms structured datasets (CSV/Excel) into rich, interactive visual reports and plain-English summaries — all without writing a single line of code.

At its core, DataNova integrates **GPT-4** for natural language data summarization, **Plotly** for dynamic infographics, and a **Figma API** pipeline for export-ready design assets. A built-in Q&A chatbot lets users interrogate their dataset in conversational language, making data exploration accessible to analysts, students, and business users alike.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📤 **Multi-format Upload** | Accepts CSV and Excel files; handles real-world messy data gracefully |
| 🤖 **GPT-4 Summaries** | Generates Executive, Technical, or Business-focused summaries contextual to the dataset |
| 📊 **Interactive Infographics** | Plotly-powered bar, line, scatter, and histogram charts with user-defined axes |
| 💬 **Conversational Q&A** | Chat interface to ask free-form questions about your data in Normal, Deep, or Quick mode |
| 🎨 **Figma Export** | Pushes visualization frames directly to Figma via the REST API for design-ready reports |
| 🌑 **Dark UI** | Polished dark-mode Streamlit interface built with custom CSS for professional presentation |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    DataNova Frontend                      │
│              (Streamlit — app.py)                        │
│   Upload → Summary Mode → Chart Builder → Chat Interface │
└──────────────────┬───────────────────────────────────────┘
                   │  REST API (requests)
┌──────────────────▼───────────────────────────────────────┐
│                  DataNova Backend                         │
│                    (api.py / main.py)                    │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ summarizer  │  │  visualizer  │  │     qna        │  │
│  │   (GPT-4)   │  │   (Plotly)   │  │   (GPT-4)      │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                         │                                │
│               ┌─────────▼──────────┐                    │
│               │  figma_exporter.py  │                    │
│               │   (Figma REST API)  │                    │
│               └────────────────────┘                    │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

**Frontend**
- [Streamlit](https://streamlit.io) — rapid Python web UI framework
- Custom CSS — dark theme, card-based layout

**Backend & AI**
- [OpenAI GPT-4](https://platform.openai.com/) — natural language summarization and Q&A
- [Plotly Express](https://plotly.com/python/plotly-express/) — interactive chart generation
- [Pandas](https://pandas.pydata.org/) — data ingestion and manipulation

**Integrations**
- [Figma REST API](https://www.figma.com/developers/api) — design export pipeline

**Deployment**
- [Render](https://render.com) — backend hosting
- Streamlit Cloud compatible

---

## 🚀 Getting Started

### Prerequisites

```bash
Python >= 3.8
OpenAI API key
Figma Personal Access Token (optional, for export)
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Slaytistics/DataNova.git
cd DataNova

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# → Add OPENAI_API_KEY, FIGMA_TOKEN, etc.

# 4. Start the backend
python main.py

# 5. Launch the Streamlit frontend
streamlit run app.py
```

### Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 access |
| `FIGMA_TOKEN` | Figma personal access token for design export |
| `BACKEND_URL` | URL of the running FastAPI/Flask backend |

---

## 📸 Usage

1. **Upload** a CSV or Excel file using the file uploader
2. **Choose Summary Style** — Executive Summary, Technical Analysis, or Business Insights
3. **Generate Summary** — GPT-4 reads your dataset and returns a contextual narrative
4. **Build Charts** — pick chart type, X/Y axes, and row limit; get an interactive Plotly graphic
5. **Chat with Your Data** — ask anything in plain English via the Q&A chatbot
6. **Export to Figma** — push visuals to your design workspace with one click

---

## 📁 Project Structure

```
DataNova/
├── app.py              # Streamlit frontend — UI layout, widgets, API calls
├── main.py             # Backend entry point
├── api.py              # REST API route definitions (/summary, /visualize, /chat)
├── summarizer.py       # GPT-4 summarization logic
├── visualizer.py       # Plotly chart generation
├── qna.py              # GPT-4 conversational Q&A over dataframe context
├── figma_exporter.py   # Figma API integration for design export
├── requirements.txt    # Python dependencies
└── .streamlit/         # Streamlit configuration (theme, server settings)
```

---

## 🔬 ML & AI Concepts Applied

- **Prompt Engineering** — Structured prompts with dynamic dataset context injected into GPT-4 calls to produce domain-specific summaries (executive vs. technical vs. business)
- **Retrieval-Augmented Generation (RAG) Pattern** — Dataset statistics and sample rows are embedded into prompts to ground the model's responses in real data
- **Conversational AI** — Multi-turn chat history management with session state, enabling coherent dialogue about the uploaded dataset
- **Data-Driven Visualization** — Automated chart-type selection and axis mapping based on column dtypes

---

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss what you'd like to change, then submit a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Built with ❤️ for democratizing data science**

*If you found this useful, please consider giving it a ⭐*

</div>
