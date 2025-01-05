FROM python:latest

WORKDIR /superlink

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn"  , "--bind", "0.0.0.0:5000", "superlink:app"]