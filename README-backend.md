# Smart CP Generator — Backend (FastAPI)

## Quickstart
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
API will be at: `http://localhost:8000`

## Endpoints
- `GET /api/health` — health check.
- `POST /api/generate` — multipart/form-data with fields:
  - `recap`: Fixture Recap `.txt`
  - `base_cp`: Base CP Template `.docx`
  - `negotiated`: Negotiated Clauses `.txt`
  - `filename` (optional): name for the generated `.docx` file

Returns a ZIP containing:
- the generated `Final_CP.docx` (or your specified `filename`), and
- a `validation_report.json` with detected conflicts, gaps, and filled placeholders.

## How it works
1. Parses recap/negotiated `key: value` pairs and fills placeholders like `{{CHARTERER}}` in the template.
2. Parses numbered clauses from the base template and merges with negotiated clauses.
3. Reports clause conflicts (same number, different text) and tries to renumber sequentially.
4. Appends a clean "Clauses" section at the end of the final document.
