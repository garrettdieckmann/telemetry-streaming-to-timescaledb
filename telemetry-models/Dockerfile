## Same base image
FROM python:3.8-slim as base

## Builder Image
FROM base as builder

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

## App Image
FROM base

RUN apt-get update \
    && apt-get -y install libpq-dev
COPY --from=builder /opt/venv /opt/venv

RUN mkdir /app
COPY main.py /app
WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"
CMD ["python", "main.py"]