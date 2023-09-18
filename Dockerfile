# Fallback Image

FROM python:3.10.13 AS fallback_base

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser
USER appuser

COPY *.py /app/
COPY mobilenet_v3_large-5c1a4163.pth /app/

EXPOSE 8000

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--log-level", "info", "--timeout", "180", "main:app" ]

# Tests for fallback

FROM fallback_base AS fallback_base_test

USER root
RUN pip install --no-cache-dir pytest httpx
USER appuser

COPY ./tests/ /app/tests/

CMD ["pytest"]

# Main image

FROM fallback_base AS main_base

COPY wide_resnet50_2-9ba9bcbe.pth /app/

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--log-level", "info", "--timeout", "180", "main:app" ]

# Tests for main 

FROM main_base AS main_base_test

USER root
RUN pip install --no-cache-dir pytest httpx
USER appuser

COPY ./tests/ /app/tests/

CMD ["pytest"]
