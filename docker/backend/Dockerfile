# Используем официальный образ Python как базовый
FROM python:3.9

ARG PROJECT_URL
ENV PROJECT_URL=${PROJECT_URL}

ARG TELEGRAM_BOT_API_TOKEN
ENV TELEGRAM_BOT_API_TOKEN=${TELEGRAM_BOT_API_TOKEN}

ARG NOWPAYMENTS_API_KEY
ENV NOWPAYMENTS_API_KEY=${NOWPAYMENTS_API_KEY}

ARG VPN_BASE_URL
ENV VPN_BASE_URL=${VPN_BASE_URL}

ARG VPN_USERNAME
ENV VPN_USERNAME=${VPN_USERNAME}

ARG VPN_PASSWORD
ENV VPN_PASSWORD=${VPN_PASSWORD}

ENV PYTHONPATH="${PYTHONPATH}:/var/www"

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /var/www

# Устанавливаем зависимости для сборки OpenSSL
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libssl-dev \
#    zlib1g-dev \
#    libncurses5-dev \
#    libncursesw5-dev \
#    libreadline-dev \
#    libsqlite3-dev \
#    libgdbm-dev \
#    libdb5.3-dev \
#    libbz2-dev \
#    libexpat1-dev \
#    liblzma-dev \
#    tk-dev \
#    libffi-dev \
#    wget

# Скачиваем и устанавливаем OpenSSL
#RUN wget https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1v/openssl-1.1.1v.tar.gz \
#    && tar -xzvf openssl-1.1.1v.tar.gz \
#    && cd openssl-1.1.1v \
#    && ./config \
#    && make \
#    && make install \
#    && ldconfig

# Удаляем архив и каталог с исходным кодом OpenSSL для уменьшения размера образа
#RUN rm -rf openssl-1.1.1v.tar.gz openssl-1.1.1v

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта в рабочую директорию
COPY . .

#RUN pip install ./libs/python-telegram-bot-master ./libs/pytonapi

# Указываем порт, на котором будет работать приложение
EXPOSE 8000 5555

COPY ./docker/supervisord/supervisord.conf /etc/supervisord.conf

## Запускаем приложение FastAPI с помощью Uvicorn
#CMD ["supervisord", "-c", "/etc/supervisord.conf"]

CMD ["uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]