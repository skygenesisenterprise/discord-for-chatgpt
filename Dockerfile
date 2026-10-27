FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv pip install --system .

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "discord_for_chatgpt.main:app", "--host", "0.0.0.0", "--port", "8000"]
