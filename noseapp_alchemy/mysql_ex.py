# -*- coding: utf-8 -*-

from copy import copy
from contextlib import contextmanager

from noseapp_alchemy import registry
from noseapp_alchemy.config import Config
from noseapp_alchemy.base import setup_engine
from noseapp_alchemy.base import setup_session
from noseapp_alchemy.constants import DEFAULT_BIND_KEY
from noseapp_alchemy.constants import DEFAULT_POOL_CLASS


DEFAULT_PORT = 3306
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PROTOCOL = 'mysql'

DEFAULT_USE_UNICODE = 1
DEFAULT_CHARSET = 'utf8'

DEFAULT_DNS_PARAMS = {
    'charset': DEFAULT_CHARSET,
    'use_unicode': DEFAULT_USE_UNICODE,
}


class MySQLClient(object):
    """
    Клиент для работы с MySQL
    """

    name = None

    def __init__(self, engine):
        self._engine = engine

    @contextmanager
    def read(self):
        """
        Выполнить sql на чтение
        """
        yield self._engine.connect().execute

    @contextmanager
    def write(self):
        """
        Выполнить sql на запись
        """
        connection = self._engine.connect()
        trans = connection.begin()
        try:
            yield connection.execute
            trans.commit()
        except:
            trans.rollback()
            raise


class MySQLEx(object):
    """
    Установщик расширения MySQL
    """

    name = 'mysql'

    client_class = MySQLClient

    def __init__(self, *configs):
        for config in configs:
            setup_engine(**config)

    @staticmethod
    def orm_session_configure(**params):
        """
        Устанавливает сессию для работы с ORM
        """
        setup_session(**params)

    def get_client(self, bind_key=DEFAULT_BIND_KEY):
        """
        Установить клиента по работе с БД, как расшрение
        для класса TestCase как расширение для NoseApp
        """
        cls = copy(self.client_class)
        cls.name = bind_key
        return cls(registry.get_engine(bind_key))


def make_config():
    """
    Создать скелет конфигурации для engine
    """
    return Config(
        db=None,
        user=None,
        password=None,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        bind_key=DEFAULT_BIND_KEY,
        protocol=DEFAULT_PROTOCOL,
        pool_class=DEFAULT_POOL_CLASS,
        dns_params=DEFAULT_DNS_PARAMS,
    )
