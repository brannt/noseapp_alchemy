# -*- coding: utf8 -*-

"""
Базовый модуль для работы с alchemy
"""

from urllib import urlencode

from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.result import exc
from sqlalchemy.orm import scoped_session

from noseapp_alchemy_ex import registry
from noseapp_alchemy_ex.session import Session
from noseapp_alchemy_ex.constants import DEFAULT_BIND_KEY
from noseapp_alchemy_ex.constants import DEFAULT_POOL_CLASS


AUTO_FLUSH = True
AUTO_COMMIT = False
EXPIRE_ON_COMMIT = True


def ping_connection(connection, connection_record, connection_proxy):
    """
    Проверяет, что соединение живое
    """
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT 1')
    except:
        raise exc.DisconnectionError()

    cursor.close()


def setup_engine(
        protocol, host, port, db, user,
        password='',
        dns_params='',
        bind_key=DEFAULT_BIND_KEY,
        pool_class=DEFAULT_POOL_CLASS,
        **engine_options):
    """
    Установить движок для работы с DB

    :param host: db хост
    :param port: db порт
    :param db: имя базы
    :param user: пользователь
    :param password: пароль
    :param protocol: протокол по которому будет выбрана стратегия работы
    :param pool_class: класс пула соединений
    :param dns_params: словарь параметров которые нужно добавить к dns
    :param engine_options: аргументы которые нужно передать в create_engine
    """
    if dns_params and isinstance(dns_params, dict):
        dns_params = '?%s' % urlencode(dns_params)

    dns = '{protocol}://{user}:{password}@{host}:{port}/{database}%s' % dns_params

    engine = create_engine(
        dns.format(
            user=user,
            host=host,
            port=port,
            database=db,
            protocol=protocol,
            password=password,
        ),
        poolclass=pool_class,
        **engine_options
    )

    if pool_class != DEFAULT_POOL_CLASS:
        event.listen(engine, 'checkout', ping_connection)

    registry.register_engine(bind_key, engine)


def setup_session(
        autoflush=AUTO_FLUSH,
        autocommit=AUTO_COMMIT,
        expire_on_commit=EXPIRE_ON_COMMIT,
        **options):
    """
    Установить сессию для работы с orm
    """
    sess = scoped_session(
        sessionmaker(
            class_=Session,
            autoflush=autoflush,
            autocommit=autocommit,
            expire_on_commit=expire_on_commit,
            **options
        ),
    )
    registry.register_session(sess)
