# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Copy dependency file(s)
COPY pyproject.toml ./
# If you have a requirements.txt file, use that instead
# COPY requirements.txt ./

# Install pip dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard] pandas sqlalchemy psycopg2-binary

# Copy the rest of your project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
