# -*- coding: utf-8 -*-
# @File  : client.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf 
# @Author: funnywolf
# @Contact : github.com/FunnyWolf

try:
    from socketserver import BaseRequestHandler
    from socketserver import ThreadingTCPServer
    import configparser as conp
except Exception as E:
    from SocketServer import BaseRequestHandler
    from SocketServer import ThreadingTCPServer
    import ConfigParser as conp

import json
import os
import sys
import time
from threading import Thread

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from config import *

global LOG_LEVEL, SLEEP_TIME, READ_BUFF_SIZE, WEBSHELL, TARGET_ADDR, LOCAL_ADDR, CLEAN_DIE, SOCKET_TIMEOUT
global cache_conns, die_client_address, not_in_server_cache_conns


# import SocketServer
# class ThreadingTCPServerReuse(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#     allow_reuse_address = True


class LoopThread(Thread):  # 继承父类threading.Thread
    def __init__(self, ):
        Thread.__init__(self)
        self.die_client_address = []

    def run(self):
        logger.warning("LoopThread start")
        while True:
            self.sync_data()
            time.sleep(SLEEP_TIME)

    def check_server(self):
        payload = {
            "Remoteserver": REMOTE_SERVER,
            "Endpoint": "/check/",

        }
        for i in range(5):
            try:
                r = requests.post(WEBSHELL, data=payload, timeout=3, verify=False)
                web_return_data = json.loads(b64decodeX(r.content).decode("utf-8"))
            except Exception as E:
                logger.error(r.content)
                logger.warning("Try to connet to server, count {}".format(i))
                time.sleep(1)
                continue
            logger.info(" ------------Server Config------------")
            logger.info(
                "\nLOG_LEVEL: {}\nREAD_BUFF_SIZE: {}\nSERVER_LISTEN: {}\nTARGET_ADDR: {}\nclient_address_list:{}\nSOCK5: {}".format(
                    web_return_data.get("LOG_LEVEL"), web_return_data.get("READ_BUFF_SIZE"),
                    web_return_data.get("SERVER_LISTEN"), web_return_data.get("TARGET_ADDR"),
                    web_return_data.get("client_address_list"),
                    web_return_data.get("SOCKS5"),
                ))

            logger.info("Connet to server success")
            return True

        logger.warning("Connet to server failed,please check server and webshell")
        return False

    def sync_data(self):
        payload = {
            "Remoteserver": REMOTE_SERVER,
            "Endpoint": "/stinger_sync/",
            "DATA": "",
            "Die_client_address": "",
        }
        data = {}
        # 清除无效的client

        for client_address in self.die_client_address:
            try:
                one = cache_conns.pop(client_address)
                one.get("conn").close()
                logger.warning("CLIENT_ADDRESS:{} close client in die_client_address".format(client_address))
            except Exception as E:
                logger.warning(
                    "CLIENT_ADDRESS:{} close client close client in die_client_address error".format(client_address))

        for client_address in list(cache_conns.keys()):
            client = cache_conns.get(client_address).get("conn")
            try:
                tcp_recv_data = client.recv(READ_BUFF_SIZE)
                logger.debug("CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(client_address, tcp_recv_data))
                if len(tcp_recv_data) > 0:
                    logger.info("CLIENT_ADDRESS:{} TCP_RECV_LEN:{}".format(client_address, len(tcp_recv_data)))
            except Exception as err:
                tcp_recv_data = b""
                logger.debug("TCP_RECV_NONE")
            data[client_address] = {"data": base64.b64encode(tcp_recv_data)}

        payload["DATA"] = b64encodeX(json.dumps(data))
        payload["Die_client_address"] = b64encodeX(json.dumps(self.die_client_address))

        try:
            r = requests.post(WEBSHELL, data=payload, verify=False)
        except Exception as E:
            logger.warning("Post data to webshell failed")
            logger.exception(E)
            return

        try:
            web_return_data = json.loads(b64decodeX(r.content))
        except Exception as E:
            # webshell 脚本没有正确请求到服务器数据或脚本本身报错
            logger.warning("Webshell return error data")
            logger.warning(r.content)
            return

        if web_return_data == WRONG_DATA:
            logger.error("Wrong b64encode data")
            logger.error(b64encodeX(json.dumps(data)))
            return

        self.die_client_address = []

        for client_address in list(web_return_data.keys()):
            try:
                client = cache_conns.get(client_address).get("conn")
                tcp_send_data = base64.b64decode(web_return_data.get(client_address).get("data"))
            except Exception as E:
                logger.warning("CLIENT_ADDRESS:{} server socket not in client socket list".format(client_address))
                self.die_client_address.append(client_address)
                continue

            try:
                client.send(tcp_send_data)
                logger.debug("CLIENT_ADDRESS:{} TCP_SEND_DATA:{}".format(client_address, tcp_send_data))
            except Exception as E:
                logger.warning("CLIENT_ADDRESS:{} Client socket send failed".format(client_address))
                self.die_client_address.append(client_address)
                try:
                    client.close()
                    cache_conns.pop(client_address)
                except Exception as E:
                    logger.exception(E)

        # 检查没有在server返回列表中的client

        if CLEAN_DIE:
            for client_address in list(cache_conns.keys()):
                if web_return_data.get(client_address) is None:
                    if cache_conns.get(client_address).get("new") is True:
                        cache_conns[client_address]["new"] = False
                        pass
                    else:
                        logger.warning(
                            "CLIENT_ADDRESS:{} remove client not in server CHCHE_CONNS".format(client_address))
                        logger.warning("CLIENT_ADDRESS:{} append in die_client_address".format(client_address))
                        self.die_client_address.append(client_address)



class TCPClient(BaseRequestHandler):
    def handle(self):
        logger.warning('Got connection from {}'.format(self.client_address))
        self.request.settimeout(SOCKET_TIMEOUT)
        key = "{}:{}".format(self.client_address[0], self.client_address[1])
        cache_conns[key] = {
            "conn": self.request,
            "new": True,  # 新的连接,第一次检查略过
        }
        while True:
            time.sleep(10)  # 维持tcp连接


if __name__ == '__main__':
    if os.path.exists("config.ini") is not True:
        print("Please copy config.ini into same folder!")
        sys.exit(1)
    configini = conp.ConfigParser()
    configini.read("config.ini")

    try:
        LOG_LEVEL = configini.get("TOOL-CONFIG", "LOG_LEVEL")
    except Exception as E:
        LOG_LEVEL = "INFO"
    logger = get_logger(level=LOG_LEVEL, name="StreamLogger")
    try:
        CLEAN_DIE_str = configini.get("TOOL-CONFIG", "CLEAN_DIE")
        if CLEAN_DIE_str.lower() == "true":
            CLEAN_DIE = True
        else:
            CLEAN_DIE = False
    except Exception as E:
        CLEAN_DIE = True
    # read_buff_size
    try:
        READ_BUFF_SIZE = int(configini.get("TOOL-CONFIG", "READ_BUFF_SIZE"))
    except Exception as E:
        logger.exception(E)
        READ_BUFF_SIZE = 51200

    try:
        SLEEP_TIME = float(configini.get("TOOL-CONFIG", "SLEEP_TIME"))
        if SLEEP_TIME <= 0:
            SLEEP_TIME = 0.1
    except Exception as E:
        logger.exception(E)
        SLEEP_TIME = 0.1


    # socket_timeout
    try:
        SOCKET_TIMEOUT = float(configini.get("TOOL-CONFIG", "SOCKET_TIMEOUT"))
    except Exception as E:
        SOCKET_TIMEOUT = 0.1
    # 获取核心参数
    try:
        WEBSHELL = configini.get("NET-CONFIG", "WEBSHELL")
        REMOTE_SERVER = configini.get("NET-CONFIG", "SERVER_LISTEN")
        LOCAL_ADDR = configini.get("NET-CONFIG", "LOCAL_ADDR")
    except Exception as E:
        logger.exception(E)
        sys.exit(1)

    try:
        REMOTE_SERVER = configini.get("ADVANCED-CONFIG", "REMOTE_SERVER")
    except Exception as E:
        logger.debug(E)
        logger.info("Use SERVER_LISTEN as REMOTE_SERVER")
    if REMOTE_SERVER.startswith("http://") is not True:
        REMOTE_SERVER = "http://{}".format(REMOTE_SERVER)

    logger.info(" ------------Client Config------------")
    logger.info(
        "\nLOG_LEVEL: {}\nSLEEP_TIME:{}\nREAD_BUFF_SIZE: {}\nWEBSHELL: {}\nREMOTE_SERVER: {}\nLOCAL_ADDR: {}\nSOCKET_TIMEOUT: {}\n".format(
            LOG_LEVEL, SLEEP_TIME, READ_BUFF_SIZE, WEBSHELL, REMOTE_SERVER, LOCAL_ADDR,SOCKET_TIMEOUT
        ))

    cache_conns = {}

    webthread = LoopThread()
    if webthread.check_server() is not True:
        sys.exit(1)

    webthread.start()

    server = ThreadingTCPServer((LOCAL_ADDR.split(":")[0], int(LOCAL_ADDR.split(":")[1])), TCPClient)
    logger.warning("Tcpserver start")
    server.serve_forever()
    logger.warning("Tcpserver exit")
