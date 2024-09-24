FROM python:3.11-alpine

ADD main.py .

RUN pip install yfinance matplotlib pandas
CMD ["python", "./main.py"]
