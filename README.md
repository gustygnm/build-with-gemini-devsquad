# 🚀 DevSquad AI — Autonomous Virtual Product & Engineering Team

![Build with Gemini](https://img.shields.io/badge/Build%20with%20Gemini-World%20Tour-4285F4?logo=google&logoColor=white)
![Track 3](https://img.shields.io/badge/Track%203-Agent--First%20Apps-EA4335)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Platform-4285F4?logo=googlecloud&logoColor=white)
![Built with ADK](https://img.shields.io/badge/Built%20with-ADK%20%2B%20agents--cli-34A853)

An agent-first application orchestrating an autonomous software product and engineering team — featuring specialized roles for **Product Management (PM)**, **UI/UX Design**, **Software Development**, **Quality Assurance (QA)**, and **Data Analysis**.

Built with Google Cloud's **Agent Platform**, **Vertex AI**, **Firestore**, **Cloud Storage**, and **Cloud Run** for Track 3 of the *Build with Gemini World Tour*.

---

## 🎬 Demo in Action

![DevSquad AI Demo](devsquad_demo.gif)

---

## 👥 The Team Personas

| Role | Responsibilities | Tools & Integrations |
|---|---|---|
| 📋 **PM (Product Manager)** | Defines user stories, backlog items, sprint tasks, and acceptance criteria. | `list_tasks`, `get_task`, `create_task`, `update_task_status` in **Firestore** |
| 🎨 **UI/UX Designer** | Designs interfaces, creates mobile/web concepts, and generates visual mockups. | `generate_design_mockup` via `gemini-3.1-flash-lite-image` & **Cloud Storage** |
| 💻 **Developer** | Implements backend/frontend logic, architectural design, and dependency analysis. | `check_pypi_package_info` (Live PyPI API) & **Agent Engine Code Sandbox** |
| 🧪 **QA Engineer** | Formulates comprehensive test suites, edge case validations, and QA acceptance tests. | Test case generation, PyPI verification, and test execution in sandbox |
| 📊 **Product Analyst** | Evaluates story point velocity, complexity metrics, and project health. | Firestore metrics calculation & sandbox analysis |

---

## 🧩 Architectural Stack

DevSquad AI connects all core building blocks introduced in the workshop:

- **Reasoning Engine (ADK)**: Python agent built with `google-adk` and `agents-cli`, deployed on Google Cloud Agent Platform.
- **Cross-Session Memory**: **Vertex AI Memory Bank** (`PreloadMemoryTool` + `add_session_to_memory`) stores project context and user architectural preferences across separate conversations.
- **Structured Persistent Storage**: **Cloud Firestore** manages the live sprint board and task backlog (`tasks` collection).
- **Public Media Storage**: **Google Cloud Storage (GCS)** stores generated UI/UX design mockups with public read URLs.
- **Generative Media**: `gemini-3.1-flash-lite-image` creates real-time UI/UX design wireframes and visual assets.
- **Isolated Code Sandbox**: **Agent Platform Sandbox Code Execution** safely runs Python logic and test verifications.
- **Live External API**: Fetches real-time package metadata and compatibility directly from the PyPI JSON API.
- **Rich Display UI**: **A2UI v0.8** generates interactive card surfaces for sprint summaries and visual deliverables.
- **Web Frontend**: A lightweight **FastAPI A2A proxy** paired with a responsive dark-mode chat interface deployed to **Cloud Run**.

---

## 🛠️ Local Development & Running

### Prerequisites
- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Google Cloud CLI (`gcloud`) with ADC configured

### 1. Run the Agent Locally
```bash
cd ai-dev-team
agents-cli install
agents-cli run "Show me the tasks currently on our project board"
```

### 2. Launch Local ADK Playground
```bash
cd ai-dev-team
agents-cli playground
# Open http://localhost:8080 in your browser
```

### 3. Run the Frontend Proxy Locally
```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
export AGENT_DIRECTORY="app"
python main.py
# Open http://localhost:8080
```

---

## 🚀 Deployment

### Deploy Agent to Agent Platform
```bash
cd ai-dev-team
agents-cli deploy
```

### Deploy Frontend to Cloud Run
```bash
cd frontend
gcloud run deploy devsquad-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="AGENT_ENGINE_RESOURCE_NAME=$AGENT_ENGINE_RESOURCE_NAME,AGENT_DIRECTORY=app"
```

---

## 📄 License
Apache License 2.0. Copyright 2026 Google LLC.
