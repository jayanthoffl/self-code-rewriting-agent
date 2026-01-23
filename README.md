# 🧬 Auto-Dev: Self-Healing AI Infrastructure

This project is an autonomous agent that monitors Python applications running in Docker. When a crash is detected, the AI reads the stack trace, analyzes the code using Google Gemini, and hot-patches the file to fix the bug in real-time.

## 🚀 Features
- **Crash Detection:** Real-time monitoring of Docker container logs.
- **AI Analysis:** Uses Google Gemini Pro to understand tracebacks.
- **Surgical Repairs:** Modifies only the broken code block.
- **Dockerized:** Fully isolated environment.

## 🛠️ Tech Stack
- **AI:** LangChain, CrewAI, Google Gemini
- **Backend:** FastAPI, Python 3.10
- **Infra:** Docker, Docker SDK, Git

## ⚡ Quick Start

1. **Clone the repo**
   ```bash
   git clone [https://github.com/your-username/auto-dev-agent.git](https://github.com/your-username/auto-dev-agent.git)
   cd auto-dev-agent
