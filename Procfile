worker: bot:app python bot.py
web: uvicorn bot:app --host 0.0.0.0 --port $PORT
web: gunicorn app:app

