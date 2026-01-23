FROM python:3.10-slim

# Force Python to print logs immediately (Fixes blank logs)
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

# ... rest of your file ...
RUN pip install watchdog
COPY . .
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
CMD ["python", "main.py"]