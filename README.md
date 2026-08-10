# Password Tool

A password generator and strength checker.
- **Backend:** Python (Flask API)
- **Frontend:** HTML, CSS, JavaScript (no frameworks)

## Files

| File | What it does |
|---|---|
| `password_tool.py` | Core logic — generates passwords and rates strength |
| `api.py` | Small web server that exposes that logic to the frontend |
| `requirements.txt` | Python packages needed to run the backend |
| `index.html` | The web page |
| `style.css` | Styling |
| `script.js` | Connects the page to the backend API |

## How to run it

**1. Install backend requirements:**
```bash
pip install -r requirements.txt
```

**2. Start the backend:**
```bash
python api.py
```
This runs the API at `http://127.0.0.1:5000`.

**3. Open the frontend:**
Open `index.html` with a live server (e.g. VS Code's "Live Server" extension) — don't just double-click it, or the page won't be able to talk to the backend.

## Notes

- `script.js` has one line at the top, `API_URL`, that tells the frontend where the backend is running. Update it if you move the backend somewhere else (like Render).
- Passwords are never saved or logged — they're only used to compute a score, then discarded.
