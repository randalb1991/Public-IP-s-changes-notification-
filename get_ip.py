import sqlite3
import logging
from json import load
from urllib2 import urlopen
import datetime
import time
import boto3
import os
path_base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_file = os.path.join(path_base, 'ips.log')
db_path = os.path.join(path_base, 'ips.db')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(lineno)s '
           '%(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
conexion = sqlite3.connect(db_path)
arn = 'arn:aws:sns:eu-west-1:533680604961:nas_house'

cursor = conexion.cursor()

def create_database():

    try:
        cursor.execute('''
                     CREATE TABLE ips (ip VARCHAR(100), date_time VARCHAR(100), time_stamp VARCHAR(100))
                     ''')
    except sqlite3.OperationalError:
        logger.debug('DataBase created before')

def get_my_public_ip():
    return load(urlopen('http://jsonip.com'))['ip']

def get_date_time():
    return datetime.datetime.now().isoformat()

def get_timestamp():
    return time.time()

def send_notification(current_ip):
    sns = boto3.resource('sns')
    topic = sns.Topic(arn)
    response = topic.publish(
        Message='Your current ip is {}'.format(current_ip),
        Subject='Your Public ip has been changed'
    )


def save_my_current_ip():
    cursor.execute("SELECT ip from ips order  by time_stamp desc")
    try:
        last_ip = cursor.fetchone()[0]
    except:
        last_ip = None
    logger.debug('Your last ip saved is {}'.format(last_ip))
    current_ip = get_my_public_ip()
    logger.debug('Your current Ip is {}'.format(current_ip).encode('utf8'))
    if (last_ip != current_ip) or (last_ip is None):
        logger.debug('Your IP is different now')
        logger.debug('Saving your current ip')
        element = (get_my_public_ip(), get_date_time(), get_timestamp())
        cursor.execute("INSERT INTO ips VALUES (?,?,?)", element)
        conexion.commit()
        logger.debug('IP saved in DB')
        send_notification(current_ip)

    else:
        logger.debug('Your last and current ip are the same...')
    conexion.close()

create_database()
save_my_current_ip()