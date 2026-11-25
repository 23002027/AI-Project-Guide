# Installation & Setup Guide — AI Project & Hackathon Co-Pilot

This guide walks you through setting up and running the application on Windows, macOS, or Linux.

---

## 1. Prerequisites

Ensure the following tools are installed on your machine:
- **Python:** 3.10 or higher (`python --version`)
- **Node.js:** v20.0.0 or higher (`node -v`)
- **Git:** Latest version (`git --version`)

---

## 2. Step-by-Step Installation

### Step A: Clone the Repository
```bash
git clone https://github.com/your-username/ai-project-copilot.git
cd ai-project-copilot
```

### Step B: Backend Configuration & Virtual Environment
```bash
# 1. Create a Python virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Create your local environment file
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

### Step C: Environment Variables (`.env`)
Open `.env` in your text editor:
```env
# Optional: Set your Anthropic API Key to enable live Claude intelligence
# For automated tests, an API key is NOT required (all tests run offline for free)
ANTHROPIC_API_KEY=your_key_here

# Security Key for JWT Authentication
JWT_SECRET_KEY=change-this-to-a-secure-random-key-in-production

# Relational Database Path
DATABASE_PATH=backend/data/copilot.db

# CORS Allowed Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step D: Frontend Installation
```bash
cd frontend

# Install dependencies
npm install

# Build to verify assets
npm run build
```

---

## 3. Running the Application Locally

### Terminal 1: Backend Server
```bash
# From the project root with (.venv) active:
python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`

### Terminal 2: Frontend Dashboard
```bash
# From the frontend/ directory:
npm run dev
```
- Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Running the Complete Automated Test Suite

The test suite runs 100% offline using mocked fixtures with zero paid API credit usage:
```bash
python -m pytest backend/tests -v
```
Expected result: **70 passed in ~8 seconds**.

> **Note for Windows Users:** If running within isolated sandbox environments where loopback socket creation is restricted, run pytest with administrative or elevated socket access (`BypassSandbox: true`).
