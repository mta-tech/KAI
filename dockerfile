FROM python:3.11.4

LABEL Author="MTA"
LABEL version="0.2.0"

# Upgrade pip and install poetry
RUN pip install --upgrade pip && pip install poetry 

# Set working directory
WORKDIR /app

# Copy only the dependency files first (for cache efficiency)
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Run the model download script
RUN poetry run python -m app.data.download_model

# Specify the entry point
ENTRYPOINT ["poetry", "run", "python", "-m", "app.main"]