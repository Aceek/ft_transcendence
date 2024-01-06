FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt
	&& python3 manage.py migrate

ENTRYPOINT ["python3", "manage.py", "runserver"]