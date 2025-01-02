import pika
import numpy as np
from sklearn.datasets import load_diabetes
import json
import time
from datetime import datetime

# Загружаем датасет
X, y = load_diabetes(return_X_y=True)

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        random_row = np.random.randint(0, X.shape[0]-1)
        time.sleep(10)
        # Подключение к серверу на локальном хосте:
        #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        #Добавляем уникальный идентификатор сообщения
        message_id = datetime.timestamp(datetime.now())
        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        #Формируем сообщение
        message_y_true = {'id': message_id, 'body': y[random_row]}
        # Публикуем сообщение
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true)
                              )
        print('Сообщение с правильным ответом отправлено в очередь')
        message_features = {'id': message_id,'body': list(X[random_row])}
        # Создаём очередь features
        channel.queue_declare(queue='features')
        # Публикуем сообщение
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features)
                                )
        print('Сообщение с вектором признаков отправлено в очередь')
        #Создаем ещё одну очередь для синхронизации циклов работы сервиса features и plot
        message_plot = {'id': message_id,'body': True}
        # Создаём очередь features
        channel.queue_declare(queue='plot')
        # Публикуем сообщение
        channel.basic_publish(exchange='',
                              routing_key='plot',
                              body=json.dumps(message_plot)
                              )
        print('Сообщение с вектором признаков отправлено в очередь')
        # Закрываем подключение
        connection.close()
    except:
        print('Не удалось подключиться к очереди')
