# ---- Builder Stage ----
# Multi-stage build to create optimized production image
FROM --platform=linux/amd64 python:3.12-slim as builder

# Set environment variables for Poetry installation and configuration
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION=2.0.1
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install Poetry and build essentials for dependency compilation
# Remove unnecessary packages after installation to minimize image size
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Set working directory for the build process
WORKDIR /app

# Copy Poetry configuration files first for better Docker layer caching
# Changes to source code won't invalidate the dependency installation layer
COPY pyproject.toml poetry.lock ./

# Configure Poetry for containerized environment:
# - Create virtual environment in project directory for easier copying
# - Install only production dependencies (--only main)
# - Disable interactive prompts and ANSI colors for CI/CD compatibility
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --only main --no-interaction --no-ansi


# ---- Final Stage ----
# Lightweight runtime image with only necessary components
FROM --platform=linux/amd64 python:3.12-slim

# Python environment variables for production:
# - Prevent Python from buffering stdout/stderr for better logging
# - Prevent Python from writing .pyc files to reduce disk usage
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory for the application
WORKDIR /app

# Create a non-root user and group for security
# Using standard user/group IDs (1001) for better compatibility with container orchestration platforms
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Copy installed Python packages from builder stage virtual environment
# This transfers only the necessary runtime dependencies without Poetry or build tools
COPY --from=builder /app/.venv/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy application source code
# Copying after dependency installation for better Docker layer caching
COPY ./src ./src

# Set proper ownership of application files for the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user for security (prevents privilege escalation)
USER appuser

# Expose the port the application listens on
# This is purely documentation - actual port binding happens at runtime
EXPOSE 8080

# Health check to verify the application is responding
# Useful for container orchestration and monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/server')" || exit 1

# Default command to run the application
# Using exec form for better signal handling in containers
CMD ["python", "src/main.py"]


