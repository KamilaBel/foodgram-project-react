# Foodgram

## Продуктовый помощник

[Foodgram](https://foodgram-yp.sytes.net)
> На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов,
необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии проекта

- Python
- PostgreSQL
- DRF
- JSON
- Docker

## Тестовый пользователь:

- email - admin@test.com
- Пароль - testmeplease

## Как запустить приложение в контейнере:

В директории /infra создайте файл .env с переменными окружения для работы с базой данных:

```
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
DB_NAME=#имя базы данных
DB_USER=#логин для подключения к базе данных
DB_PASSWORD=# пароль для подключения к БД
APP_HOME=/var/www/foodgram
DJANGO_SECRET_KEY=
```

Выполнить команду:
```
docker-compose -f infra/docker-compose.yml up -d
```

## Документация к проекту.

После запуска приложения документация доступна по адресу:

```
http://localhost/api/docs/
```

## Некоторые примеры запросов к API.

Регистрация пользователя.

```
POST /api/users/
```

REQUEST:

```
{
  "email": "user@yandex.ru",
  "username": "User",
  "first_name": "Иван",
  "last_name": "Сидоров",
  "password": "Pass123"
}
```
