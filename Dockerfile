FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY src/ src/

RUN uv pip install --no-cache-dir --system .

CMD ["rembrandt-chat"]
