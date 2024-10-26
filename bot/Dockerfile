FROM python:3.12-bullseye

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /bot

COPY poetry.lock pyproject.toml ./

RUN pip install poetry==1.5.1

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY ./bot .
