FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY dashboard.py .

ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=80", "--server.address=0.0.0.0"]
