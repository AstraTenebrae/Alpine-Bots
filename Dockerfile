FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN echo "#!/bin/bash\n\
python manage.py collectstatic --noinput\n\
python manage.py migrate\n\
gunicorn --bind 0.0.0.0:\$PORT bot_constructor.wsgi:application" > entrypoint.sh

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]