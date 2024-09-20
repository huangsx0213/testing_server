FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 确保 gunicorn 在路径中
ENV PATH="/usr/local/bin:${PATH}"
EXPOSE 8088
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "app:app"]