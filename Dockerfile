FROM python:3-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 8080

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "wsgi:app" ]
