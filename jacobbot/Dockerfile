FROM python:3.11-slim

WORKDIR /app

COPY run.sh /run.sh
COPY bot.py /app/bot.py
COPY data /app/data

RUN pip install slack_bolt slack_sdk
RUN chmod +x /run.sh

CMD ["/run.sh"]
