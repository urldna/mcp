# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install uv (no pip needed later)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

# Copy project metadata first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies into the system environment
RUN uv sync --frozen --no-install-project --no-dev

# Copy project files
COPY . .

# Expose port
EXPOSE 8080

# Run your FastMCP server using uv
ENTRYPOINT ["uv", "run", "python", "urldna_mcp/server.py"]