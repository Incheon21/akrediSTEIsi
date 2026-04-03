FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no project itself yet)
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Install the project itself
RUN uv sync --frozen

EXPOSE 8000

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
