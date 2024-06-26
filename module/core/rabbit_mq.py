import pika
import json
import uuid
from time import sleep,time
from datetime import datetime
from pika.exceptions import ConnectionClosed
import requests

from .customlogger import logger
from .db_sqlalchemy import Database

from module.settings import CONEXAO_RABBIT


class ExitMessage(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class MaxWaitError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MessageSender:
    
    def __init__(self, 
                queue_name: str, 
                username:str = CONEXAO_RABBIT['USER'],
                password:str = CONEXAO_RABBIT['PASSWORD'],
                host:str = CONEXAO_RABBIT['HOST'],
                port:int = CONEXAO_RABBIT['PORT'],
                vhost:str = CONEXAO_RABBIT['VHOST'],
                ):
        self.queue_name = queue_name
        self.connection = None
        
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.vhost = vhost
        
        if self.vhost == '/': self.vhost_api = '%2f'
        else: self.vhost_api = vhost
        
        self.base_url = 'http://192.168.3.75:15672/api'
        
        self.queue_url = f'{self.base_url}/queues/{self.vhost_api}/{self.queue_name}'
        
        self.consumers = 0
    
    def __enter__(self):
        if not self.connection or self.connection.is_closed:
            self.credentials = pika.PlainCredentials(self.username,self.password)
            self.parameters = pika.ConnectionParameters(self.host,self.port,self.vhost,self.credentials)
            self.connection = pika.BlockingConnection(self.parameters)
            
            self.channel = self.connection.channel()
            
            self.callback_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
            self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self._on_response, auto_ack=True)

    def __exit__(self):
        if self.connection or self.connection.is_open:
            self.connection.close()
    
    def check_consumers(self,api=False):
        logger.info(f'Checking consumers in Queue: {self.queue_name}')
        
        if api: return self.get_queue_info_api()
        else: return self.get_queue_info()
        
    def get_queue_info_api(self):
        for _ in range(60):
            response = requests.get(self.queue_url, auth=(self.username, self.password))
            if response.ok:
                queue_info = response.json()
                if 'consumers' in list(queue_info.keys()):
                    self.consumers = int(queue_info['consumers'])
                    logger.info(f"A fila {self.queue_name} tem {self.consumers} consumidores ativos.")
                    return self.consumers
            else: sleep(1)
        else: return None
    
    def get_queue_info(self):
        try: 
            self.__enter__()
            queue_info = self.channel.queue_declare(queue=self.queue_name, passive=True)
            self.consumers = queue_info.method.consumer_count
            logger.info(f"A fila {self.queue_name} tem {self.consumers} consumidores ativos.")
            return self.consumers
        except: raise
        finally: self.__exit__()
    
    def _on_response(self, ch, method, props, body):
        if self.correlation_id == props.correlation_id:
            self.response = json.loads(body)

    def _publish(self, message):
        self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.correlation_id,
                ),
                body=json.dumps(message)
            )
        
    def send_message(self, message: dict, wait_response = True, wait_time = 1):
        try:       
            self.__enter__() 
            
            self.response = None
            self.correlation_id = str(uuid.uuid4())

            logger.debug(message)
            
            self._publish(message)

            start_time = time()
            if wait_response:
                while self.response is None:
                    self.connection.process_data_events()
                    time_atual = time()
                    
                    if bool(wait_time):
                        if time_atual >= start_time + (wait_time*60):
                            raise MaxWaitError(
                                f'Tempo máximo aguardando resposta do broker: wait_time = {wait_time} minutes')
                            
                return self.response
            
        except ConnectionClosed:
            self.__enter__()
            self.send_message(message, wait_response) 
            
        finally: self.__exit__()

    def _publish_exit(self, message):
        self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                ),
                body=json.dumps(message)
            )
        
    def send_exit_message(self):
        try:
            self.__enter__()
            self.response = None

            message = {
                'exit': True
            }
            
            self._publish_exit(message)
        
        except ConnectionClosed:
            self.__enter__()
            self._publish_exit(message)
        
        finally: self.__exit__()


class MessageConsumer:
    
    def __init__(self, 
                queue_name: str, 
                prefech_count: int=1,
                exclusive=True, 
                durable=True,
                username:str = CONEXAO_RABBIT['USER'],
                password:str = CONEXAO_RABBIT['PASSWORD'],
                host:str = CONEXAO_RABBIT['HOST'],
                port:int = CONEXAO_RABBIT['PORT'],
                vhost:str = CONEXAO_RABBIT['VHOST'],
                ):
        self.db = Database()
        self.queue_name = queue_name
        self.prefech_count = prefech_count
        self.exclusive = exclusive
        self.durable = durable
        self.connection = None
        
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.vhost = vhost
        
        if self.vhost == '/': self.vhost_api = '%2f'
        else: self.vhost_api = vhost

        self.base_url = 'http://192.168.3.75:15672/api'
        
        self.queue_url = f'{self.base_url}/queues/{self.vhost_api}/{self.queue_name}'
        
    def __enter__(self):
        if not self.connection or self.connection.is_closed:
            self.credentials = pika.PlainCredentials(self.username,self.password)
            self.parameters = pika.ConnectionParameters(self.host,self.port,self.vhost,self.credentials)
            self.connection = pika.BlockingConnection(self.parameters)
            
            self.channel = self.connection.channel()
            
            if self.prefech_count:
                self.channel.basic_qos(prefetch_count=self.prefech_count)
            
            self.channel.queue_declare(queue=self.queue_name, exclusive=self.exclusive, durable=self.durable)

    def __exit__(self):
        if self.connection or self.connection.is_open:
            self.connection.close()
    
    def _process_message(self, ch, method, props, body: dict):
        
        status = None
        log = None
        rowcount = 0
        
        try:
            message = json.loads(body)
            # Processar a mensagem recebida aqui
            
            if 'query' in message.keys():
                rowcount = self.db.run_query(message['query'])
            
            status = 'C'
            log = 'Success'
            
        except Exception as e:
            
            status = 'E'
            log = e
            
        finally:
            
            response = {
                '_id': props.correlation_id,
                'status': status,
                'log': log,
                'data': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                'message': message,
                'rowcount': rowcount
                }
            
            logger.debug(response)
            
            ch.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id=props.correlation_id),
                body=json.dumps(response)
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            if 'exit' in message.keys():
                if message['exit']: 
                    logger.info(f'Deleting Queue: {self.queue_name}')
                    self.channel.queue_delete(queue=self.queue_name)
                    raise ExitMessage(f'Message exit: {message}')
            
    def start_consuming(self):
        self.__enter__()
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._process_message)
        self.channel.start_consuming()
        self.__exit__()


if __name__ == '__main__':
    # Enviar mensagem
    sender = MessageSender('minha_fila')
    message = {'nome': 'João', 'idade': 30}
    response = sender.send_message(message)
    print('Resposta recebida:', response)

    # Consumir mensagem
    consumer = MessageConsumer('minha_fila')
    consumer.start_consuming()