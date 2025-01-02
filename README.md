Домашнее задание №1 (HW)
# RabbitMQ
Business Usage - MicroServices - RabbitMQ

Шаг 1.
- Добавлена задержка после каждой итерации на 10 сек, чтобы можно было отслеживать происходящее
- Добавлен в каждое сообщение уникальный идентификатор message_id для возможности идентификации всех данных всех микросервисов в рамках каждой итерации

Шаг 2.
- В папке logs/ создается и далее пополняется данными файл metric_log.csv.
- В данный файл сохраняются метрики message_id, y_true, y_pred, absolute_error
- При этом значения y_true, y_pred одной итерации идентифицируются и связываются с помощью message_id

Шаг 3.
- Добавлен к архитектуре ещё один сервис — plot.
- Сервис plot считывает данные из metric_log.csv и создает график error_distribution.png

Шаг 4.
- Создан файл docker-compose.yaml который указывает порядок запуска микросервисов внутри docker контейнера
- Далее в терминале собран docker образ с помощью команды: docker-compose build
- Далее запущен контейнер из данного образа: docker-compose up -d
- Контроль работы сервисов можно осуществлять с помощью команд:
        - docker ps
        - docker-compose logs -f features
        - docker-compose logs -f model
        - docker-compose logs -f metric
        - docker-compose logs -f plot
