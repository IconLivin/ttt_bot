FROM python

WORKDIR /app

COPY . .

RUN ["pip", "install", "pytelegrambotapi"]

CMD ["python", "main.py"]