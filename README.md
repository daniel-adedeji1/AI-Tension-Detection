# AI Tension Detection

AI Tension Detection is a capstone project that combines a React dashboard, a Django backend, and an edge-processing pipeline for detecting high-tension incidents from bodycam-style audio and video streams.

## What is in this repo

- `frontend/`: React + Vite UI for login, manager monitoring, and employee learning flows.
- `backend/`: Django + Django REST Framework backend with session auth, alert APIs, and WebSocket broadcasts.
- `ai-detection-model/`: Python edge pipeline and test harness for simulated incident detection over ZeroMQ.

## Architecture

- The frontend runs locally in the browser and calls the backend at `http://localhost:8000`.
- The backend stores users and alerts in SQLite by default and exposes WebSocket alerts at `ws://localhost:8000/ws/alerts/`.
- The edge pipeline can send alert events over ZeroMQ so the backend can surface them in the manager dashboard.

## Tech stack

- Frontend: React 19, Vite, React Router, Tailwind CSS
- Backend: Django, Django REST Framework, Daphne, Channels
- AI pipeline: Python 3.12, TensorFlow, OpenCV, ZeroMQ

## Prerequisites

- Node.js 18+ and npm
- Python 3.12 recommended
- `pip` for the backend environment
- `uv` for the `ai-detection-model` module

## Quick start

If you only want to run the web app locally, start the backend and frontend.

### 1. Start the backend

Open a terminal in `backend/`:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and run migrations:

```bash
pip install -r requirements.txt channels
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`.

### 2. Start the frontend

Open a second terminal in `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

Vite will print a local URL, usually `http://localhost:5173`.

## How to use the app

- Open the frontend in your browser.
- Register a user from the `New Employee Registration` page, then log in with the generated employee ID and password.
- Manager users land on the operations dashboard.
- Non-manager users land on the learning portal.

For quick UI-only testing, the login page also includes mock routing:

- Any employee ID containing `MANAGER` or `ADMIN` routes to the manager view.
- Any employee ID containing `EMP` routes to the employee learning view.

## Optional: run live alert ingestion

If you want the manager dashboard to receive live alerts, run the backend plus the ZMQ listener.

Open a third terminal in `backend/` with the backend virtual environment activated:

```bash
cd backend
python manage.py run_zmq_listener
```

This listens for ZeroMQ packets on `tcp://*:5556` and forwards supported alert events to WebSocket clients.

### Send test alerts

With the backend and listener running, you can simulate incoming alerts from another terminal:

```bash
cd backend
python backend/mock_alert.py
```

Then log into the manager dashboard and watch alerts appear in real time.

## Optional: run the edge AI pipeline

The `ai-detection-model/` directory is a separate Python module with its own dependencies and README. It is intended for the bodycam/AI portion of the project.

Open a terminal in `ai-detection-model/`:

```bash
cd ai-detection-model
uv sync
```

To run the local harness:

```bash
uv run python minimal_test_harness.py
```

To run the edge pipeline in demo mode:

```bash
uv run python edge_pipeline.py --demo-mode
```

The module-level guide with more detail is here: [`ai-detection-model/README.md`](./ai-detection-model/README.md)

## Useful backend notes

- The backend uses SQLite by default for local development.
- WebSocket alerts use Django Channels. The default local configuration uses an in-memory channel layer, so Redis is not required for basic development.
- If you switch to a Redis-backed channel layer, also install `channels-redis` and provide `REDIS_HOST` / `REDIS_PORT`.
- The backend reads optional environment variables from `.env` if present.

Examples:

```env
ENABLE_ALERT_TEST_ENDPOINT=true
AUTO_START_ZMQ_LISTENER=false
CHANNEL_LAYER_BACKEND=inmemory
ZMQ_INGEST_BIND_ADDRESS=tcp://*:5556
ZMQ_INGEST_CONNECT_ADDRESS=tcp://127.0.0.1:5556
```


## Project structure

```text
AI-Tension-Detection/
|-- ai-detection-model/
|-- backend/
|-- docs/
|-- frontend/
`-- README.md
```

## Recommended startup order

1. Start `backend/`
2. Start `frontend/`
3. Optionally start `python manage.py run_zmq_listener`
4. Optionally start `python backend/mock_alert.py` or the edge pipeline
