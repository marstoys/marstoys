# Python 3.12 slim versiyasidan foydalanamiz
FROM python:3.12-slim

# Ishchi katalogni belgilash
WORKDIR /app

# Optimallashtirilgan Python sozlamalari
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Kerakli fayllarni ko'chirish va kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha boshqa fayllarni ko'chirish
COPY . .

# Static fayllarni collect qilish (Django uchun)
RUN python manage.py collectstatic --noinput


EXPOSE 8000

# Gunicorn yordamida Django ilovasini ishga tushirish
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
