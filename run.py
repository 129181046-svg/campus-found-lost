# run.py
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # use_reloader=False fixes a known Windows + Python 3.13
    # socket error in Werkzeug's reloader thread.
    # Auto-reload is a dev convenience only — this has zero
    # effect on production (Render uses gunicorn, not this file).
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)