FROM python:3.10-bullseye

EXPOSE 80

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install

COPY . /app

COPY .env /app/.env

RUN poetry run aerich upgrade

VOLUME [ "/attachments", "/data" ]
CMD [ "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]