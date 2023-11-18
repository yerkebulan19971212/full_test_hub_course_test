FROM python:3.10.2


RUN set -x; \
    apt-get update; \
    apt-get install -y --no-install-recommends wkhtmltopdf;

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
