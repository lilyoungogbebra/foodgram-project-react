# Foodgram
![Foodgram-project-react](https://github.com/lilyoungogbebra/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Адрес приложения:

```
http://51.250.29.141/
```

## Описание проекта:
Проект Foodgram продуктовый помощник - платформа для публикации рецептов.
Cайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

 * Реализован бекенд.
 * Фронтенд - одностраничное приложение, которое взаимодействовует с API через удобный пользовательский интерфейс (разработан Яндекс.Практикум).

### БД и статика (только после первого деплоя)
Подключаемся к серверу через ssh и выполняем миграции БД.
```
sudo docker-compose exec web python manage.py makemigrations
sudo docker-compose exec web python manage.py migrate
```
Собираем статические файлы
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
По желанию, загружаем фикстуры
```
sudo docker-compose exec web python manage.py loaddata fixtures.json
```

### Запуск проекта на сервере
## Для работы сервиса, на сервере должем быть установлен docker и docker-compose.
- Клонируйте репозиторий командой:
```
git clone git@github.com:lilyoungogbebra/foodgram-project-react.git
``` 
- Перейдите в каталог командой:
```
cd foodgram-project-react/backend/
``` 
- Выполните команду для запуска контейнера:
```
docker-compose up -d
``` 
- Выполните миграции:
```
docker-compose exec web python manage.py migrate --noinput
``` 
- Команда для сбора статики:
```
- docker-compose exec web python manage.py collectstatic --no-input
``` 
- Команда для создания суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
``` 

### Авторы
Frontend: Yandex Practicum
Backend: lilyoungogbebra (Yan)
