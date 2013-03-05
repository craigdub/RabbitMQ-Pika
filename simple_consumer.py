import pika
import logging
import logging.config

#configure my logger
logging.config.fileConfig('log.conf')

#holds channel objects
channel = None

#all of the following functions run in precedential order
def on_connected(connection):
    """We are now connected to rabbit_mq"""

    #lets open a chennel which is used to communicate with rabbitmq exchanges
    connection.channel(on_channel_open)

def on_channel_open(new_channel):
    """Once the channel has been opened, we can now declare a queue"""
    global channel
    channel = new_channel

    channel.queue_declare(queue="my_queue_name", durable=True, exclusive=False, auto_delete=False, callback=on_queue_declared)

def on_queue_declared(frame):
    """Once rabbitmq has told us our queue was declared, set the consumer handler name and queue"""
	channel.basic_consume(receive_message, queue='my_queue_name', no_ack=True)

try:
	#get the name of the logger in my configuration
	logger = logging.getLogger('logger_name')

	#get the handler for my logger so it knows where to write to 
	iHndlr = logger.handlers[0]

	#set credentials for rabbitmq-server
	credentials = pika.PlainCredentials('rabbit_username','rabbit_password')

	connection = pika.BlockingConnection(
					pika.ConnectionParameters(
						'hostname',
						5762),
						credentials=credentials)
					)

	channel = connection.channel()

except Exception as e:
	logger.error('Something went wrong... %s', e)

def receive_message(ch, method, properties, body):
    """Called when we receive a message from RabbitMQ"""
	logging.info('Received a message!  This is what it is %s', body)

try:
	#start consuming messages!
	channel.start_consuming()
except Exception as e:
	logger.error('Something went wrong... %s', e)
