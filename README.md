# ⚡ AutoDev v2.0: Autonomous Self-Healing Infrastructure

<div align="center">

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)
![React](https://img.shields.io/badge/React-18-cyan.svg)
![Docker](https://img.shields.io/badge/Container-Docker%20SDK-blue)
![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Llama-purple)
![Status](https://img.shields.io/badge/System-Operational-success)

<h3>The Code That Fixes Itself.</h3>

<p>
  A next-generation <strong>Autonomous DevOps Agent</strong> that reduces Mean Time to Recovery (MTTR) to zero. <br>
  AutoDev deploys applications in isolated sandboxes, monitors runtime telemetry, and autonomously generates, tests, and commits code patches when crashes occur.
</p>

[View Demo](#-screenshots) • [Installation](#-installation--setup) • [Architecture](#-system-architecture) • [Contribute](#-contributing)

</div>

---

## 📖 Overview

In traditional software development, a runtime crash requires a human engineer to wake up, read logs, reproduce the error, and push a fix. **AutoDev v2.0 automates this entire lifecycle.**

By combining **Containerization (Docker)** with **Large Language Model (LLM) reasoning**, AutoDev acts as an always-on "Site Reliability Engineer." It doesn't just report errors; it understands them. Upon detecting a `Traceback`, the system pauses execution, extracts the stack trace, and instantiates a virtual "Senior Python Developer" agent. This agent analyzes the codebase, formulates a syntactic and logical patch, applies it to the file system, and pushes the resolution to GitHub—all without human intervention.

---

## 📸 Interface

![Dashboard Preview](https://via.placeholder.com/800x400?text=AutoDev+Mission+Control+Interface)
*The Matrix-style "Mission Control" dashboard provides real-time telemetry streaming, visual status indicators, and manual override controls.*

---

## ⚙️ How It Works (The "Loop")

AutoDev operates on a closed-loop control system inspired by biological self-healing mechanisms:

1.  **Deployment & Isolation:**
    The user submits a repository URL. AutoDev clones the source code into a temporary workspace and dynamically generates a `Dockerfile`. The application is spun up in a sandboxed Docker container with strict resource limits.

2.  **Telemetry Stream Analysis:**
    The backend attaches to the container's `stdout/stderr` streams. A regex-based heuristic engine scans for critical failure patterns (e.g., `ZeroDivisionError`, `KeyError`, `ModuleNotFoundError`).

3.  **Context-Aware Diagnosis:**
    Upon crash detection, the system triggers the **AI Agent**. The agent is fed:
    * The complete Stack Trace.
    * The content of the file implicated in the crash.
    * A prompt engineered for "Root Cause Analysis."

4.  **Generative Patching:**
    The LLM (Gemini 1.5 Flash or Llama 3.3) computes a solution. Instead of returning text, it utilizes **Function Calling** to execute file system operations, rewriting the specific lines of code causing the issue.

5.  **Verification & Commit:**
    The patched code is saved, and the container is hot-reloaded (or restarted). If the patch stabilizes the application, GitPython authenticates with the repository and pushes a commit tagged `🩹 Auto-fix: AI Agent repaired the crash`.

---

## 🧠 System Architecture

The solution is built on a microservices architecture to ensure separation of concerns between the UI, the Orchestrator, and the Execution Runtime.

### 1. The Neural Core (Backend)
Built with **FastAPI** and **Python 3.10**, the backend serves as the central nervous system.
* **Asynchronous Task Queue:** Uses `BackgroundTasks` to handle long-running Docker builds without blocking the API.
* **Docker SDK Integration:** Manages the lifecycle of ephemeral containers, ensuring no zombie processes are left behind.
* **CrewAI Framework:** Orchestrates the AI agents, defining specific roles ("Senior Developer"), goals ("Fix runtime errors"), and backstories to ground the LLM's reasoning.

### 2. The Visual Cortex (Frontend)
A high-performance Single Page Application (SPA) built with **React** and **Vite**.
* **Real-Time Polling Engine:** Fetches state deltas every 1000ms to provide a "live terminal" experience.
* **Tailwind CSS System:** Implements a custom "Cyber-Security" design language with neon accents and dark-mode defaults.
* **State Management:** Handles transient states (`DEPLOYING`, `CRASHED`, `FIXING`) to give the user immediate visual feedback on the agent's decision-making process.

---

## 🛠️ Prerequisites

Before initiating the sequence, ensure your environment meets these specifications:

* **Docker Desktop:** Version 4.15+ (Must be running and accessible via `/var/run/docker.sock`).
* **Node.js:** Version 18.x (LTS recommended).
* **Python:** Version 3.10 or higher.
* **Access Credentials:**
    * **LLM Provider:** `OPENROUTER_API_KEY` or `GOOGLE_API_KEY` (The brain power).
    * **Version Control:** `GITHUB_TOKEN` (Classic PAT with `repo` read/write permissions).

---

## 🚀 Installation & Setup

### 1. Clone the Infrastructure
```bash
git clone [https://github.com/jayanthoffl/self-code-rewriting-agent.git](https://github.com/jayanthoffl/self-code-rewriting-agent.git)
cd self-code-rewriting-agent
