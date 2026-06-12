FROM python:3.11-slim AS builder

WORKDIR /build
COPY 05-scaling-reliability/production/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim AS runtime

RUN groupadd -r agent && useradd -r -g agent -m -d /home/agent agent
WORKDIR /app

COPY --from=builder /root/.local /home/agent/.local
COPY 05-scaling-reliability/production/app.py .
RUN mkdir -p utils
COPY 05-scaling-reliability/production/utils/mock_llm.py utils/mock_llm.py

RUN chown -R agent:agent /app
USER agent

ENV PATH=/home/agent/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
