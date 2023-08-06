FROM python:3.10-slim

COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "app.py"]