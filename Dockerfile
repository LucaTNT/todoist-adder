FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# gunicorn's control server needs a writable HOME, so create one
RUN useradd --create-home --shell /usr/sbin/nologin --uid 1001 todoist-adder
USER todoist-adder

EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--threads", "4", "main:app"]
