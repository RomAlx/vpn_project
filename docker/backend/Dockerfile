# Используем официальный образ Python как базовый
FROM python:3.9

ENV PYTHONPATH="${PYTHONPATH}:/var/www"

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /var/www

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта в рабочую директорию
COPY . .

# Указываем порт, на котором будет работать приложение
EXPOSE 8000 5555

COPY ./docker/supervisord/supervisord.conf /etc/supervisord.conf

CMD ["uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]