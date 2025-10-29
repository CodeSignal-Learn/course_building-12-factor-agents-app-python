## Overview

Minimal FastAPI server with an agent and a simple HTTP client.

## Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the server

From the `src` directory:

```bash
cd src
python -m uvicorn server.main:app --host 0.0.0.0 --port 3000 --reload
```

This exposes the API at `http://localhost:3000`.

Endpoints:
- `POST /agent/launch`
- `POST /agent/resume`

## Run the client

From the `src` directory (ensures the `core` package is on the module path):

```bash
cd src
python -m client.main
```

Alternatively, from the repository root using `PYTHONPATH`:

```bash
PYTHONPATH=src python src/client/main.py
```

## Notes

- Always run from `src` or set `PYTHONPATH=src` so imports like `core.*` work.
- The client sends a request to `http://localhost:3000/agent/launch`.

