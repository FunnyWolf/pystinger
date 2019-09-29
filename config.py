# -*- coding: utf-8 -*-
# @File  : config.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf
# @Author: funnywolf
# @Contact : github.com/FunnyWolf
import base64
import logging
import logging.config

# 错误码
DATA = "DATA"
WRONG_DATA = b"WRONG DATA"  # 错误格式的数据
INVALID_CONN = b"REMOVE CONN"  # 无效的连接
SOCKET_TIMEOUT = 0.01


# 	data = strings.Replace(strings.Replace(data, "\r\n", "", -1), "\n", "", -1)
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
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'logging.log',
                'level': 'DEBUG',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'StreamLogger': {
                'handlers': ['console'],
                'level': level,
            },
            'FileLogger': {
                'handlers': ['file'],
                'level': level,
            },
        }
    }

    logging.config.dictConfig(logconfig)
    logger = logging.getLogger(name)

    return logger


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
        print(data)
        return base64.b64decode(data)


def b64encodeX(data):
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
        print(new_data)
        return new_data
