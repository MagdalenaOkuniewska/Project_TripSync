FROM python:3.14-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt-get update

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "src/manage.py", "runserver"]
