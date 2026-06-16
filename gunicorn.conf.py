# gunicorn.conf.py

workers = 1          # Free tier: only 1 worker to stay within 512MB
threads = 2          # 2 threads per worker
timeout = 120        # 120 seconds before killing a stuck worker
worker_class = "sync"
bind = "0.0.0.0:10000"