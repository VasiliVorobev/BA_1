import pika
import pickle
import numpy as np
import json
import sklearn

with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    #Укажем, с какой очередью будем работать:
    channel.queue_declare(queue='features')

    #Напишем функцию callback(), определяющую, как работать с полученным сообщением
    def callback(ch, method, properties, body):
        print(f'Получен вектор признаков {json.loads(body)}')
        #Парсим сообщение из очереди и записываем в файл metric_log.csv
        body_tmp = json.loads(body.decode('utf-8'))
        features = body_tmp.get('body')
        message_id = body_tmp.get('id')
        pred = regressor.predict(np.array(features).reshape(1, -1))
        message_y_pred = {'id': message_id,'body': pred[0].tolist()}
        channel.basic_publish(exchange='',
                              routing_key='y_pred',
                              body=json.dumps(message_y_pred)
                              )
        print(f'Предсказание {message_y_pred} отправлено в очередь y_pred')

    # Извлекаем сообщение из очереди features
    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except:
    print('Не удалось подключиться к очереди')
