FROM python:latest

WORKDIR /superlink

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./superlink.py" ]