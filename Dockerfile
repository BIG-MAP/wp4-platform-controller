FROM python:3.11.3-slim AS base

ADD . /app

WORKDIR /app
RUN pip install poetry

FROM base

RUN poetry install

ENV PYTHONUNBUFFERED=1
ENV PORT=9000
ENV LLE_API_SETTINGS_PATH=/app/lle_settings.json
ENV LLE_API_URL=http://lle:8000
ENV PLC_API_URL=opc.tcp://plc:4840

EXPOSE $PORT

CMD ["bash", "-c", "poetry run uvicorn controller.api:app --port $PORT --host 0.0.0.0"]