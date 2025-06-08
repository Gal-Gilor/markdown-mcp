# ---- Builder Stage ----
FROM --platform=linux/amd64 python:3.12-slim as builder

# Set environment variables for Poetry
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION=2.0.1
# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install Poetry and build essentials
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create the virtualenv in the project's root
# and install dependencies directly without using requirements.txt or export.
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-interaction --no-ansi


# ---- Final Stage ----
FROM --platform=linux/amd64 python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Create a non-root user and group
# Using standard user/group IDs for better compatibility (e.g., with OpenShift)
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Copy installed packages from the builder stage's virtual environment
COPY --from=builder /app/.venv/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy the application source code
# Ensure this path matches your project structure
COPY ./src ./src

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "src/main.py"]
