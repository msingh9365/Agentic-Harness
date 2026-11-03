# ETL Doctor web UI. One container: the API, the page, and the runs (background tasks).
# State (checkpoints, run logs, built cases) lives in /data: mount a persistent volume there.
ARG BASE=python:3.13-slim
FROM ${BASE}

RUN pip install --no-cache-dir uv==0.11.32
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PYTHONUNBUFFERED=1

WORKDIR /app
# Dependencies first, in their own layer: code changes don't reinstall them.
# The dev group (pytest) is kept: the fault injector runs the pipeline's quality tests.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project
COPY src ./src
COPY evals ./evals
COPY demo_pipeline ./demo_pipeline
RUN uv sync --frozen

# Run as an unprivileged user; only /data and the patch output dir are writable.
RUN useradd --create-home --uid 10001 app && mkdir -p /data /app/.etl_doctor && chown app /data /app/.etl_doctor
USER app

ENV PATH="/app/.venv/bin:$PATH" \
    ETLDOC_DATA_DIR=/data \
    ETLDOC_RESUME_ON_START=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"
# Binding 0.0.0.0 needs a login: set ETLDOC_UI_USERS=name:password[,...] as a secret.
CMD ["etl-doctor", "serve", "--host", "0.0.0.0", "--port", "8000"]
