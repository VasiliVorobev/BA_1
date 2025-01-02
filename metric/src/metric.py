import pika
import pandas as pd
import json
import os.path

def metric_log(id_, y_, y_type_):
    file_path = '../../logs/metric_log.csv'
    if os.path.exists(file_path):
        try:
            df_metric = pd.read_csv(file_path)
        except Exception as e:
            print(f'Ошибка при чтении файла {file_path}: {e}')
            return
    else:
        df_metric = pd.DataFrame(columns=['message_id', 'y_true', 'y_pred', 'absolute_error'])

    # Проверяем есть ли уже сохраненные данные с таким id_message
    index = df_metric['message_id'] == id_
    if any(index):
        # Обновить значения y_true и y_pred по уже имеющейся записи
        if y_type_ == 'y_true':
            df_metric.loc[index, 'y_true'] = y_
            df_metric.loc[index, 'absolute_error'] = abs(y_ - df_metric.loc[index, 'y_pred'])
        else:
            df_metric.loc[index, 'y_pred'] = y_
            df_metric.loc[index, 'absolute_error'] = abs(df_metric.loc[index, 'y_true']-y_)
    #Запись не найдена, добавляем новую запись с имеющимися данными y_true или y_pred
    else:
        df_metric.loc[len(df_metric)] = [
            id_,
            y_ if y_type_ == 'y_true' else None,
            y_ if y_type_ == 'y_pred' else None,
            None
        ]
    # Сохранить изменения обратно в CSV-файл
    df_metric.to_csv(file_path, index=False)

try:
    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    print('Соединение установлено')
    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')
        #Парсим сообщение из очереди и записываем в файл metric_log.csv
        body_tmp = json.loads(body.decode('utf-8'))
        body_parsed = body_tmp.get('body')
        message_id = body_tmp.get('id')
        metric_log(message_id, body_parsed, 'y_true' if method.routing_key == 'y_true' else 'y_pred')

    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(
        queue='y_true',
        on_message_callback=callback,
        auto_ack=True
    )
    # Извлекаем сообщение из очереди y_pred
    channel.basic_consume(
        queue='y_pred',
        on_message_callback=callback,
        auto_ack=True
    )

    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except:
    print('Не удалось подключиться к очереди')