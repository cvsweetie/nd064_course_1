FROM python:3.8

WORKDIR /app
COPY techtrends/ /app

RUN pip install -r requirements.txt && python init_db.py

EXPOSE 3111

CMD ["python","app.py"]
