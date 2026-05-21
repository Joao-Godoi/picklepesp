FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app

WORKDIR /app

RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd app && python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "cd app && python manage.py migrate && python manage.py seed_tournament && python manage.py create_admin && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
