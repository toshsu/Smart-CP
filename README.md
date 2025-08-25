# Smart CP Generator (Full Project)

An end-to-end example project that generates a finalized Charter Party (CP) document by merging:
- Fixture Recap (`.txt`),
- Base CP template (`.docx` with placeholders like `{{CHARTERER}}`), and
- Negotiated Clauses (`.txt` with numbered clauses).

## What you get
- **Backend** (FastAPI) to parse inputs, detect conflicts/gaps, and output a final `.docx` + `validation_report.json` inside a ZIP.
- **Frontend** (static HTML/JS) to upload files and download the generated bundle.
- **Sample files** to try immediately.

## Run the backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## Open the frontend
Just open `frontend/index.html` in your browser (or serve the `frontend` folder with any static server).
Make sure the backend is running on `http://localhost:8000`.

## Try it fast with samples
In the frontend, click the links under **Sample Files** to view the examples.
Then upload:
- `backend/sample/fixture_recap.txt`
- `backend/sample/negotiated_clauses.txt`
- `backend/sample/base_cp.docx`

Click **Generate** and download the `cp_bundle.zip`.

## Notes
- Placeholder filling is rules-first. Add placeholders in your `.docx` as `{{PLACEHOLDER_NAME}}`.
- Clause conflicts are reported when the same clause number has different text between base and negotiated.
- Renumbering is kept simple and sequential for the top level.

## Extend
- Add richer NLP (e.g., spaCy) for entity extraction from freeform recaps.
- Persist versions and audit logs in a database (e.g., Postgres).
- Enhance the frontend to preview the generated doc and the JSON report.
