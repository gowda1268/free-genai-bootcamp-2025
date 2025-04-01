# Guardrails Service
FROM python:3.10-slim as guardrails

WORKDIR /app

COPY guardrails/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY guardrails/ .

CMD ["uvicorn", "guardrails:app", "--host", "0.0.0.0", "--port", "8000"]

# LLM Client Service
FROM python:3.10-slim as llm-client

WORKDIR /app

COPY llm-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY llm-server/ .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]