FROM python:3.11-alpine

WORKDIR /opt/app

COPY src/ /opt/app/

RUN pip install --no-cache-dir -r /opt/app/requirements.txt

ENTRYPOINT ["python", "app.py"]