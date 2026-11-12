ARG REG=mcr
ARG DOM=microsoft.com
FROM ${REG}.${DOM}/playwright/python:v1.55.0-noble
WORKDIR /app
COPY . .
RUN pip install requests playwright
EXPOSE 8000
CMD ["python", "bot.py"]
