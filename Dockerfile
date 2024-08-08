FROM python:3.11.4

LABEL Author="MTA"
LABEL version="0.0.1"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Set default CORE_PORT to 80 if not provided
ARG CORE_PORT=80
ENV CORE_PORT=${CORE_PORT}

EXPOSE ${CORE_PORT}

CMD ["sh", "-c", "uvicorn app.app:app --host 0.0.0.0 --port $CORE_PORT"]