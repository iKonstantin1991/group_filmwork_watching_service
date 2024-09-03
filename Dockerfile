FROM python:3.10

COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY .. .

RUN uv sync --frozen

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
