FROM python:3.11-slim AS build

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=build /usr/local /usr/local

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

ENV DJANGO_SETTINGS_MODULE=bot_constructor.settings \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "bot_constructor.wsgi:application", "--bind", "0.0.0.0:8000"]
