# Albom
Данный проект создан для прокачки собственных скиллов в веб-разработке на Flask.
Сам же сайт представляет собой социальную сеть для фотографов.
К сожалению, пока нет возможности выгрузить и запустить свой сайт на всеобщее обозрение в интернет.
Все упирается в финансы, а откуда у бедного студента деньги))
Поэтому внизу будет небольшая демонстрация сайта

## Elasticsearch
Запуск Elasticsearch:

sudo /etc/init.d/elasticsearch start

## Redis
Запуск Redis с указанием порта:

redis-server --port 6380

## Celery
Запуск Celery worker с собственным экземпляром приложения и логированием:

celery -A celery_worker.celery worker -l info

## Демонстрация
![Image alt](https://github.com/Nik148/Albom/raw/master/doc/1.png)
![Image alt](https://github.com/Nik148/Albom/raw/master/doc/2.png)
![Image alt](https://github.com/Nik148/Albom/raw/master/doc/3.png)
![Image alt](https://github.com/Nik148/Albom/raw/master/doc/4.png)
