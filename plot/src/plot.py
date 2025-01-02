import pika
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import json

def make_gistogram():
    file_path = '../../logs/metric_log.csv'
    plot_path = '../../logs/error_distribution.png'
    if os.path.exists(file_path):
        try:
            df_metric_csv = pd.read_csv(file_path)
        except Exception as e:
            print(f'Ошибка при чтении файла {file_path}: {e}')
            return
    else:
        print('Файл metric_log.csv отсутствует')
        return

    plt.figure(figsize=(10, 6))
    sns.histplot(df_metric_csv['absolute_error'], kde=True, color="orange")
    plt.savefig(plot_path)

try:
    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='plot')

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')
        make_gistogram()

    # Извлекаем сообщение из очереди features
    channel.basic_consume(
        queue='plot',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except:
    print('Не удалось подключиться к очереди')

