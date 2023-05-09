FROM python:3.11.3-slim 

ADD . /app

WORKDIR /app
RUN pip install poetry
RUN poetry install

ENV PYTHONUNBUFFERED=1
ENV PORT=9000
ENV LLE_API_SETTINGS_PATH=/app/lle_settings.json

EXPOSE $PORT

CMD ["uvicorn", "controller.main:app", "--port", $PORT]