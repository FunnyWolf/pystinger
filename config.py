# -*- coding: utf-8 -*-
# @File  : config.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf
# @Author: funnywolf
# @Contact : github.com/FunnyWolf
import base64
import json
import logging
import logging.config
import socket
import sys

LOCALADDR = "127.0.0.1"

# ERROR_CODE
ERROR_CODE = "error_code"
DEFAULT_SOCKET_TIMEOUT = 0.2

# url route
URL_SET_CONFIG = "/set_config/"
URL_CHECK = "/check/"
URL_STINGER_SYNC = "/data_sync/"
URL_CMD = "/cmd/"
# args mark
DATA_TAG = "data"
DIE_CLIENT_ADDRESS_TAG = "close_clients"

MIRROR_DATA_TAG = "mirror_data"
MIRROR_DIE_CLIENT_ADDRESS_TAG = "mirror_close_clients"

RETURN_DATA = "return_data"
MIRROR_RETURN_DATA = "mirror_return_data"

CONFIG_TAG = "tag"
CONFIG_DATA = "data"

WAIT_TIME = "wait"

CONTROL_PORT = [60010, 60011, 60012, 60013, 60014]
MIRROR_PORT = [60020, 60021, 60022, 60023, 60024]

# Buffer size to use when calling socket.recv()
BUFSIZE = 51200

# Number of connections to keep in backlog when calling socket.listen()
BACKLOG = 200

# Version code in server responses (Should always be 0 as specified in the SOCKS4 spec)
SERVER_VN = 0x00

# Version number specified by clients when connecting (Should always be 4 as specified in the SOCKS4 spec)
CLIENT_VN = 0x04

# SOCKS request codes as specified in the SOCKS4 spec
REQUEST_CD_CONNECT = 0x01
REQUEST_CD_BIND = 0x02

# SOCKS response codes as specified in the SOCKS4 spec
RESPONSE_CD_REQUEST_GRANTED = 90
RESPONSE_CD_REQUEST_REJECTED = 91


def get_logger(level="INFO", name="StreamLogger"):
    logconfig = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'StreamLogger': {
                'handlers': ['console'],
                'level': level,
            },
        }
    }

    logging.config.dictConfig(logconfig)
    logger = logging.getLogger(name)
    return logger


class NewJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode(encoding='utf-8', errors="ignore")
        return json.JSONEncoder.default(self, obj)


def diyDecode(data):
    web_return_data = json.loads(b64decodeX(data))
    return web_return_data


def diyEncode(data):
    web_return_data = b64encodeX(json.dumps(data, cls=NewJsonEncoder))
    return web_return_data


def b64decodeX(data):
    if isinstance(data, str):
        new_data = data.replace("\r\n", "")
        new_data = new_data.replace("\n", "")
        new_data = new_data.replace("-A", "+")
        new_data = new_data.replace("-S", "/")
        return base64.b64decode(new_data)
    elif isinstance(data, bytes):
        new_data = data.replace(b"\r\n", b"")
        new_data = new_data.replace(b"\n", b"")
        new_data = new_data.replace(b"-A", b"+")
        new_data = new_data.replace(b"-S", b"/")
        return base64.b64decode(new_data)
    else:
        return base64.b64decode(data)


def b64encodeX(data):
    if sys.version_info.major == 3 and isinstance(data, str):
        data = data.encode(encoding="UTF-8", errors="ignore")
    new_data = base64.b64encode(data)
    if isinstance(new_data, str):
        new_data = new_data.replace("+", "-A")
        new_data = new_data.replace("/", "-S")
        return new_data
    elif isinstance(new_data, bytes):
        new_data = new_data.replace(b"+", b"-A")
        new_data = new_data.replace(b"/", b"-S")
        return new_data
    else:
        return new_data


def port_is_used(port, ip=LOCALADDR):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False
