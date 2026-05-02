# ⚡ TeamFlow — AI-Powered Team Collaboration Platform

> **PromptWars Challenge**: Design a platform that improves team coordination and communication. The system should simplify workflows and improve visibility of tasks.

[![Deploy on Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-blue?logo=googlecloud)](https://cloud.google.com/run)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-green?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🏗️ Architecture

```
Cloud Run (Managed)
├── Flask Backend (Gunicorn)
│   ├── /api/projects   — Project CRUD
│   ├── /api/tasks      — Task CRUD + Kanban
│   ├── /api/messages   — Team Chat
│   └── /api/ai/*       — Gemini AI Features
├── Firestore (NoSQL Database)
└── Gemini 2.0 Flash (AI Engine)
```

## 🚀 Google Cloud Services Used

| Service | Purpose |
|---------|---------|
| **Cloud Run** | Serverless container hosting |
| **Cloud Firestore** | Real-time NoSQL database |
| **Gemini AI (google-genai)** | AI-powered features |
| **Cloud Build** | CI/CD pipeline |
| **Secret Manager** | Secure API key storage |
| **Cloud Logging** | Structured application logs |
| **Container Registry** | Docker image storage |

## 🤖 AI Features (Gemini Integration)

1. **Task Summarizer** — AI-generated project status reports
2. **Smart Suggestions** — Auto-generate tasks from project description
3. **Meeting Notes** — Generate structured notes from team chat
4. **Sentiment Analysis** — Analyze team morale and communication

## 📁 Project Structure

```
├── main.py                 # Entry point
├── Dockerfile              # Container config
├── cloudbuild.yaml         # CI/CD pipeline
├── requirements.txt        # Dependencies
├── app/
│   ├── __init__.py         # App factory
│   ├── config.py           # Configuration
│   ├── models/             # Data models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── utils/              # Validators & security
├── static/                 # Frontend assets
│   ├── css/style.css       # Design system
│   └── js/                 # Application JS
├── templates/index.html    # SPA shell
└── tests/                  # Unit tests
```

## 🛠️ Local Development

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Set environment variables
export FLASK_ENV=development
export GEMINI_API_KEY=your_key_here

# 3. Run locally
python main.py

# 4. Run tests
pytest tests/ -v
```

## ☁️ Deploy to Cloud Run

```bash
# Source-based deploy (simplest)
gcloud run deploy teamflow \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=your_key"

# Or use Cloud Build CI/CD
gcloud builds submit --config=cloudbuild.yaml
```

## 🔒 Security Features

- **Input Sanitization**: HTML stripping via bleach
- **CSP Headers**: Content Security Policy on all responses
- **Rate Limiting**: Per-IP request throttling
- **XSS Prevention**: Output escaping in frontend
- **CSRF Protection**: JSON content-type enforcement

## ♿ Accessibility (WCAG 2.1 AA)

- Semantic HTML5 with ARIA labels
- Keyboard navigation support
- Skip-to-content link
- High contrast color scheme
- Screen reader compatible
- Focus management in modals

## 📊 API Reference

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/:id` | Get project |
| PUT | `/api/projects/:id` | Update project |
| DELETE | `/api/projects/:id` | Delete project |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/:id/tasks` | List tasks |
| POST | `/api/projects/:id/tasks` | Create task |
| PUT | `/api/tasks/:id` | Update task |
| PATCH | `/api/tasks/:id/status` | Update status |
| DELETE | `/api/tasks/:id` | Delete task |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/:id/messages` | List messages |
| POST | `/api/projects/:id/messages` | Send message |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/summarize` | Summarize tasks |
| POST | `/api/ai/suggest-tasks` | Suggest tasks |
| POST | `/api/ai/meeting-notes` | Generate notes |
| POST | `/api/ai/sentiment` | Analyze sentiment |

## 📄 License

MIT License — see [LICENSE](LICENSE) file.
