FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir \
	Django==6.1.2 \
	djangorestframework==3.18.3 \
	python-dotenv==1.2.4

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
