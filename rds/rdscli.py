import redis
from redis.exceptions import ConnectionError
import logging
from configparser import ConfigParser
from datetime import datetime
import logging
import pickle
import json

logger = logging.getLogger(__name__)
logfile = 'logs/service_'+str(datetime.now().date()).replace('-','')+'.log'
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   
handler = logging.FileHandler(logfile)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

config_object = ConfigParser()
config_object.read("fromWFtoJET-config.ini")
redis_info = config_object["REDIS"]
redis_host = redis_info["host"]
redis_port = int(redis_info["port"])
redis_db = int(redis_info["db"])
redis_socket_keepalive = eval(redis_info["socket_keepalive"])
redis_retry_on_timeout = eval(redis_info["retry_on_timeout"])
redis_health_check_interval = int(redis_info["health_check_interval"])



class redisClient(object):
    """
        Object used to handle Client connections to Redis server.

        Attributes
        ----------
        redis_host : string
            Redis Hostname.
        redis_port : int
            Redis Port.
        redis_db : int
            Integer related to the db index to be connected with.
        redis_socket_keepalive : bool
            True if socket keepalive is required.
        redis_retry_on_timeout : bool
            True to retry connection after timeout.
        redis_health_check_interval : int
            Seconds interval for connection health check.

        Methods
        -------
        connect
            Builds the connection and generate PubSub object.
        get_message
            Retrieves messages from Redis Channel.
        publish_message
            Publishes a new message to a specific channel.
        get_bio_signatures
            Gets the current signatures stored in key-store


    """
    def __init__(self, redis_host, redis_port, redis_db, redis_socket_keepalive, redis_retry_on_timeout, redis_health_check_interval):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_socket_keepalive = redis_socket_keepalive
        self.redis_retry_on_timeout = redis_retry_on_timeout
        self.redis_health_check_interval = redis_health_check_interval
        logger.info("[Redis] Redis Client built")
    
    def connect(self, channel):
        """
            Performs connection to Redis and generate PubSub object.

            Parameters
            ----------
            channel : string
                channel to be subscribed to.
        """
        self.pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db, socket_keepalive=self.redis_socket_keepalive,
                                    retry_on_timeout=self.redis_retry_on_timeout, health_check_interval=self.redis_health_check_interval)
        self.r = redis.Redis(connection_pool=self.pool)
        self.ps = self.r.pubsub()
        self.ps.psubscribe(channel)
        logger.info("[Redis] Connected and subscribed to {0}".format(channel))

    def get_message(self, channel_pattern, only_messages=True):
        """
            Retrieves messages from Redis Channel pattern.

            Parameters
            ----------
            channel_pattern : string
                channel pattern form which to collect messages.
            only_messages: bool
                True to filter out subscription messages.

            Returns
            ----------
            msg
                the message. None in case of no message
        """
        try:
            msg = self.ps.get_message()
            if msg:
                if only_messages:
                    if msg['type'] == 'pmessage':
                        return msg
                else:
                    return msg
            else:
                return None
        except ConnectionError:
            logger.info("[Redis] Lost connection. Try to reconnect..")
            self.connect(channel_pattern)
            msg = self.ps.get_message()
            if msg:
                if only_messages:
                    if msg['type'] == 'pmessage':
                        return msg
                else:
                    return msg
            else:
                return None
                
    def publish_message(self, channel_in, channel_out, data):
        """
            Publishes new message to a channel. Manages reconnection in case of disconnection.

            Parameters
            ----------
            channel_in : string
                The channel that the class is listening to. (in case of reconnection with pubsub)
            channel_out: string
                The channel to be used to push message.
            data : bytearray
                The message data

        """
        try:
            self.r.publish(channel_out, data)
        except ConnectionError:
            logger.info("[Redis] Lost connection. Try to reconnect..")
            self.connect(channel_in)
            self.r.publish(channel_out, data)

    def get_bio_signatures(self, key):
        """
            Function to retrieving signatures found by gateways in key-store:
            Signature pattern:
            {'<id>':{'name': '<name>', 'surname':'<surname>', 'signature': [...]}, ...}

            Parameters
            ----------
            key : string
                Key assigned to signatures dictionary

            Returns
            ----------
            signatures : dict
                Dictionary containing the persisted signatures

        """
        signaturesdumps = self.r.get(key)
        if signaturesdumps is not None:
            signatures = json.loads(signaturesdumps)
            return signatures
        else:
            None

    def set_bio_signatures(self, key, signatures):
        """
            Function to set signatures:
            Signature pattern:
            {'<id>':{'name': '<name>', 'surname':'<surname>', 'signature': [...]}, ...}

            Parameters
            ----------
            key : string
                Key assigned to signatures dictionary

            Returns
            ----------
            signatures : dict
                Dictionary containing the persisted signatures

        """
        signatures = json.dumps(signatures)
        self.r.set(key, signatures)

            
        
        

rdscli = redisClient(redis_host, redis_port, redis_db, redis_socket_keepalive, redis_retry_on_timeout, redis_health_check_interval)
        
    
