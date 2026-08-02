FROM python:3.11.9-slim

RUN useradd --create-home --uid 1000 mlflow
WORKDIR /app

RUN pip install --no-cache-dir mlflow==3.15.0

RUN mkdir -p /mlflow-data /mlflow-artifacts && \
    chown -R mlflow:mlflow /mlflow-data /mlflow-artifacts /app

USER mlflow

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:////mlflow-data/mlflow.db", \
     "--artifacts-destination", "/mlflow-artifacts", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--allowed-hosts", "*"]