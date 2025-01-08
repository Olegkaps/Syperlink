FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /superlink

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["gunicorn"  , "--bind", "0.0.0.0:5000", "superlink:app"]