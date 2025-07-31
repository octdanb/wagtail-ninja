FROM python:3.12-slim AS development
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH /code/:$PYTHONPATH
WORKDIR /code/

COPY uv.lock pyproject.toml ./
RUN uv sync && uv pip install psycopg2-binary

CMD ["tail", "-f", "/dev/null"]
