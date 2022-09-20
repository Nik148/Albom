# Albom
Данный проект создан для прокачки собственных скиллов в веб-разработке на Flask.
Сам же сайт представляет собой социальную сеть для фотографов.

## Elasticsearch
Запуск Elasticsearch:

sudo /etc/init.d/elasticsearch start

## Redis
Запуск Redis с указанием порта:

redis-server --port 6380

## Celery
Запуск Celery worker с собственным экземпляром приложения:

celery -A celery_worker.celery worker -l info
