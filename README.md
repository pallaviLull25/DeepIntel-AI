# DeepIntel

DeepIntel is a competitive research agent with a React dashboard and a FastAPI backend. Enter a market or company topic, and the app generates a structured report with a summary, competitor breakdown, market trends, recommendations, chart data, grounded evidence, and coverage gaps.

## Run

Prerequisites: Node.js and Python 3

```bash
npm install
python3 -m pip install -r requirements.txt
cp .env.example .env.local
```

Set `GEMINI_API_KEY` in `.env.local`, then start the app:

```bash
npm run dev
```

Open `http://localhost:3000`.

For a production-style run that serves the built frontend from FastAPI:

```bash
npm run preview
```

To run the local evaluation dataset against the live agent:

```bash
npm run eval:research
```

## Tech Used

- Frontend: React 19, TypeScript, Vite, Tailwind CSS 4
- UI libraries: `motion`, `recharts`, `react-markdown`, `lucide-react`
- Backend: FastAPI, Uvicorn, Pydantic, `python-dotenv`
- Agent/LLM: `google-genai` with Gemini and the Google Search tool
- Retrieval: local corpus persistence, chunking, hybrid lexical/semantic passage retrieval, and full-page fetch ingestion under `backend/retrieval/` and `backend/tools/`
- Evaluation: JSONL dataset and CLI runner under `backend/evals/`
- Dev tooling: `concurrently`

## Architecture

See [architecture.mmd](./architecture.mmd).
