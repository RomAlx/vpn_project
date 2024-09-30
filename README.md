# Ton Project

---

## Начало работы

### Запуск локально

1. Создайте .env и заполните его по примеру .env.example
2. Запустите локальный тунель командой:  
```./runlt.sh```
3. Скопируйте ссылку в .env файл:  
```PROJECT_DEV_URL```
4. Соберите frontend: 
   - ```cd frontend```
   - ```npm run build```
5. Запуск проекта:
   - Первый раз:
     ```make build_dev```
   - В последующие разы:
    ```make dev```

> При изменение переменных окружения (```.env```) или порядка сборки проекта необходимо удалить
> - остановить контейнеры
> - контейнер проекта из Docker
> - образ контейнера из Docker
> - запустить ```make dev_build```

6. Применение миграций:
   - Перейти в контейнер tonproject-python:<br>
   ```docker exec -it vpn-python /bin/bash```
   - Перейти в папку backend внутри контейнера: <br> 
   ```cd backend```
   - Cоздать миграцию: <br>
   ```alembic revision --autogenerate -m "Название миграции"```
   - Применить миграции: <br>
   ```alembic upgrade head```
   - Выйти из контейнера: <br>
   ```exit```

---

## Подключение к базе данных

> База данных также находится в контейнере. 
> Это значит что внутри контейнеров связь происходит на порту 3306, а из вне подключение производится на порту 33061

Для подключения к базе данных используйте встроенные возможности среды разработки:
- Для **PyCharm** - это встроенный инструмент <br>
_Он находится в правом верхнем углу IDE_
- Для **VS code** - это плагин [**Database Client**](https://database-client.com/#/home)