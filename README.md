## ЯндексПрактикум. Спринт 14 - "Foodgram"

<div align="center">
  <img src="https://media.giphy.com/media/dWesBcTLavkZuG35MI/giphy.gif" width="600" height="300"/>
</div>

---

![workflow](https://github.com/ViktorAllayarov/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)

## Технологиии:

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/) == 3.7  
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/) == 3.2.19  
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/) == 3.14.0
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/) == 20.1.0  
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

---

## Описание проекта:

Проект — Foodgram, «Продуктовый помощник». В этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

✅ Главная страница
http://158.160.31.116

✅ Админка
http://158.160.31.116/admin/

login: admin  
password: admin

✅ Документация к проекту
http://158.160.31.116/api/docs/

---

## Подготовка и запуск проекта (на удаленном сервере Ubuntu)

- Клонируем проект:

```
git clone git@github.com:ViktorAllayarov/foodgram-project-react.git
```

- Устанавливаем docker и docker-compose:

```
sudo apt install docker.io
sudo apt install docker-compose
```

- Cоздаем .env файл и вписываем данные:

```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
```

- Копируем файлы на сервер сервер:

```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```

- Запускаем docker-compose:

```
sudo docker-compose up -d --build
```

- Выполняем миграции, создаем суперюзера и собераем статику:

```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
