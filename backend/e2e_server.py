"""Arranca la API para los tests end-to-end de Playwright.

Borra la base SQLite de la ejecucion anterior para empezar siempre desde
cero; las tablas las crea la propia app al arrancar (evento startup).
Uso: python e2e_server.py [puerto]
"""

import sys
from pathlib import Path

import uvicorn

Path("e2e.db").unlink(missing_ok=True)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    uvicorn.run("app.main:app", host="127.0.0.1", port=port)
