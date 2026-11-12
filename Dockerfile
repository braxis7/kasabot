FROM ://microsoft.com
WORKDIR /app
COPY . .
RUN pip install requests
EXPOSE 8000
CMD ["python", "bot.py"]
