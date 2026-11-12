FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install requests playwright && playwright install --with-deps chromium
EXPOSE 8000
CMD ["python", "bot.py"]
