# Production Deployment Guide — AI Project & Hackathon Co-Pilot

This guide explains how to deploy the AI Project & Hackathon Co-Pilot application to production using Docker, Render, Railway, or Vercel.

---

## 1. Option 1: Docker Compose (Single-Command Local or VPS Deployment)

The repository includes a production-grade multi-stage `Dockerfile.backend`, `Dockerfile.frontend`, and `docker-compose.yml`.

### Deployment Steps:
```bash
# 1. Clone repository on your VPS (Ubuntu/Debian)
git clone https://github.com/your-username/ai-project-copilot.git
cd ai-project-copilot

# 2. Configure environment file
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY and a secure JWT_SECRET_KEY

# 3. Build and launch containers
docker-compose up -d --build
```

- **Frontend:** `http://your-server-ip:3000` (Nginx serving React 19 production build)
- **Backend:** `http://your-server-ip:8000` (FastAPI + Uvicorn)
- **Health Check:** `http://your-server-ip:8000/api/health`

---

## 2. Option 2: Render (Backend) + Vercel (Frontend)

### A. Deploy FastAPI Backend on Render
1. Create a free account at [Render](https://render.com).
2. Connect your GitHub repository.
3. Select **New Web Service** and point to `render.yaml` or configure manually:
   - **Environment:** Python 3.10
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/api/health`
4. Add Environment Variables:
   - `ANTHROPIC_API_KEY`: Your live Anthropic API key
   - `JWT_SECRET_KEY`: A cryptographically secure random string
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:3000`

### B. Deploy React Frontend on Vercel
1. Create a free account at [Vercel](https://vercel.com).
2. Import the `frontend/` directory.
3. The included `vercel.json` automatically configures Vite builds and rewrites `/api/*` requests to your Render backend.
4. Set Build Settings:
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Deploy!

---

## 3. Production Security Checklist

- [x] **No Plaintext Passwords:** PBKDF2-HMAC-SHA256 with 100,000 iterations.
- [x] **No Hardcoded Secrets:** All credentials dynamically read from environment variables.
- [x] **CORS Isolation:** CORS restricted to production domain and local development ports.
- [x] **Multi-Tenant Authorization:** Ownership checked on all project mutations.
- [x] **Safe File Streaming:** PPTX and Markdown downloads stream with strict MIME types.
