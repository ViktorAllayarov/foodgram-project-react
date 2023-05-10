FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

# RUN chmod +x entry_point.sh
# ENTRYPOINT ["/app/entry_point.sh"]

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]