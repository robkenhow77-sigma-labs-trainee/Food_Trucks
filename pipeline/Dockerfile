FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pipeline.py .

COPY extract.py .

COPY transform.py .

CMD ["python3", "pipeline.py"]