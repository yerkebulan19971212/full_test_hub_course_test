FROM python:3.10.2


RUN set -x; \
    apt-get update; \
    apt-get install -y --no-install-recommends wkhtmltopdf;

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN python manage.py collectstatic --noinput

COPY . /app/

CMD ["gunicorn", "--bind", ":8000", "--workers", "9", "config.wsgi:application"]
