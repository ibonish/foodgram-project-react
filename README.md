# praktikum_new_diplom

![status badge](https://github.com/ibonish/foodgram-project-react/actions/workflows/main.yaml/badge.svg)

Развернутый проект:
http://45.87.246.221/signin

Документация:
http://45.87.246.221/redoc/

# Возможности 
Данный сервис позволяет делиться рецептами с другими пользователями, с возможностью подписаться на понравившегося автора или добавления рецепта в избранное/список покупок.

# CI и CD проекта foodgram
* Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) 
* Сборка и доставка докер-образа для контейнера backend на Docker Hub
* Автоматический деплой проекта на боевой сервер
* Отправка уведомления в Telegram о том, что процесс деплоя успешно завершился


# Подготовка сервера
Установка docker и docker-compose:
```
apt update && apt upgrade
```
```
apt install docker.io
```
```
apt install docker-compose-plugin
```

# Запуск проекта
```
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

создать суперпользователя
```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
