# -*- coding: utf-8 -*-
# @File  : server.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf 
# @Author: funnywolf
# @Contact : github.com/FunnyWolf

########### only for python2.7 because pyinstaller

import os
import threading
import time
from SocketServer import BaseRequestHandler
from SocketServer import ThreadingTCPServer
from socket import AF_INET, SOCK_STREAM
from threading import Thread

from bottle import request, route, run as bottle_run

from config import *

global serverGlobal


def handle_socks_data(server_socket_conn, tcp_send_data, client_address):
    # 发送数据
    send_flag = False
    for i in range(3):
        if tcp_send_data == '':
            # 无数据发送跳出
            send_flag = True
            break
        try:
            server_socket_conn.settimeout((i * 10 + 1) * serverGlobal.SOCKET_TIMEOUT)
            server_socket_conn.sendall(tcp_send_data)
            if len(tcp_send_data) > 0:
                serverGlobal.logger.info(
                    "CLIENT_ADDRESS:{} TCP_SEND_LEN:{}".format(client_address, len(tcp_send_data)))
            send_flag = True
            break
        except Exception as E:  # socket 已失效
            serverGlobal.logger.warning("CLIENT_ADDRESS:{} Client send failed".format(client_address))
            serverGlobal.logger.exception(E)

    if send_flag is not True:
        try:
            server_socket_conn.close()
            serverGlobal.CHCHE_CONNS.pop(client_address)
        except Exception as E:
            serverGlobal.logger.exception(E)
        return

    # 读取数据 tcp数据
    revc_flag = False
    try:
        tcp_recv_data = server_socket_conn.recv(serverGlobal.READ_BUFF_SIZE)
        serverGlobal.post_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
        serverGlobal.logger.debug(
            "CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(client_address, tcp_recv_data))
        if len(tcp_recv_data) > 0:
            serverGlobal.HAS_DATA = True
            serverGlobal.logger.info(
                "CLIENT_ADDRESS:{} TCP_RECV_LEN:{}".format(client_address, len(tcp_recv_data)))
        revc_flag = True
    except Exception as err:
        pass
    if revc_flag is not True:
        tcp_recv_data = b""
        serverGlobal.post_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
        serverGlobal.logger.debug("TCP_RECV_NONE")


class MirrorRequestHandler(BaseRequestHandler):
    def handle(self):
        serverGlobal.logger.info('Got connection from {}'.format(self.client_address))
        self.request.settimeout(serverGlobal.SOCKET_TIMEOUT)
        key = "{}:{}".format(self.client_address[0], self.client_address[1])
        serverGlobal.MIRROR_CHCHE_CONNS[key] = {"conn": self.request}
        while True:
            time.sleep(0.1)  # 维持tcp连接


class ServerGlobal(object):
    def __init__(self):
        self.CHCHE_CONNS = {}
        self.MIRROR_CHCHE_CONNS = {}
        self.READ_BUFF_SIZE = BUFSIZE
        self.SOCKET_TIMEOUT = DEFAULT_SOCKET_TIMEOUT
        self.LOG_LEVEL = "INFO"
        self.NO_LOG = True
        if self.NO_LOG:
            self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
        else:
            self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")

        self.SERVER_LISTEN = None
        self.MIRROR_LISTEN = None
        self.HAS_DATA = False
        self.WAIT = 0
        self.post_return_data = {}

    def set(self, tag, data):
        """设置服务端参数"""
        if tag == "LOG_LEVEL":
            self.LOG_LEVEL = data
        elif tag == "READ_BUFF_SIZE":
            self.READ_BUFF_SIZE = data
        elif tag == "SOCKET_TIMEOUT":
            self.SOCKET_TIMEOUT = data
        elif tag == "LOG_LEVEL":
            self.LOG_LEVEL = data
            if self.NO_LOG:
                self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
            else:
                self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
        elif tag == "NO_LOG":
            if self.NO_LOG:
                self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
            else:
                self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
            self.NO_LOG = data
        else:
            return False
        self.logger.warning("server config set, TAG :{}　DATA:　{}".format(tag, data))
        return True

    def cmd(self, tag, data):
        if tag == "CLEAN_SOCKET":  # 清理所有现存的连接
            try:
                for key in serverGlobal.CHCHE_CONNS.keys():
                    one = serverGlobal.CHCHE_CONNS.pop(key)
                    self.logger.warning("Close time begin:　{}".format(time.time()))
                    one.get("conn").close()
                    self.logger.warning("Close time end:　{}".format(time.time()))
                serverGlobal.logger.info("Clean exist sockets")
                return True
            except Exception as E:
                serverGlobal.logger.exception(E)
                return False
        else:
            serverGlobal.logger.warn("Unknow cmd :{}".format(tag))
            return False


class ControlCenter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def run(self):
        serverGlobal.logger.warning("WebServer start on {}".format(serverGlobal.SERVER_LISTEN))
        bottle_run(host=serverGlobal.SERVER_LISTEN.split(":")[0],
                   port=int(serverGlobal.SERVER_LISTEN.split(":")[1]),
                   quiet=True,
                   # server='twisted'
                   )
        serverGlobal.logger.warning("WebServer exit")

    @staticmethod
    def _get_post_data(request):
        try:
            unformat_SENDDATA = request.forms.get("SENDDATA")
            serverGlobal.logger.debug(unformat_SENDDATA)
            senddata = diyDecode(unformat_SENDDATA)
        except Exception as E:
            serverGlobal.logger.exception(E)
            return None
        return senddata

    @staticmethod
    @route('/')
    def index():
        return '<b>Hello World</b>!'

    @staticmethod
    @route(URL_SET_CONFIG, method='POST')
    def set_config():
        """参数设置函数"""
        try:
            senddata = ControlCenter._get_post_data(request)
            # 获取数据错误
            if senddata is None:
                web_return_data = {ERROR_CODE: "Can not get data from post request"}
                return diyEncode(web_return_data)

            tag = senddata.get(CONFIG_TAG)
            data = senddata.get(CONFIG_DATA)
            result = serverGlobal.set(tag, data)
            return diyEncode(result)
        except Exception as E:
            serverGlobal.logger.exception(E)
            web_return_data = {ERROR_CODE: str(E)}
            return diyEncode(web_return_data)

    @staticmethod
    @route(URL_CMD, method='POST')
    def run_cmd():
        """命令执行函数"""
        try:
            serverGlobal.logger.warn("run_cmd in")
            senddata = ControlCenter._get_post_data(request)

            # 获取数据错误
            if senddata is None:
                web_return_data = {ERROR_CODE: "Can not get data from post request"}
                return diyEncode(web_return_data)

            tag = senddata.get(CONFIG_TAG)
            data = senddata.get(CONFIG_DATA)
            result = serverGlobal.cmd(tag, data)
            serverGlobal.logger.warn("run_cmd out")
            return diyEncode(result)
        except Exception as E:
            serverGlobal.logger.exception(E)
            web_return_data = {ERROR_CODE: str(E)}
            return diyEncode(web_return_data)

    @staticmethod
    @route(URL_CHECK, method='POST')
    def check():
        """自检函数"""
        serverGlobal.logger.debug("CHCHE_CONNS : {}".format(len(serverGlobal.CHCHE_CONNS)))
        # 返回现有连接
        key_list = []
        for key in serverGlobal.CHCHE_CONNS:
            key_list.append(key)

        mirror_key_list = []
        for key in serverGlobal.MIRROR_CHCHE_CONNS:
            mirror_key_list.append(key)

        data = {
            "client_address_list": key_list,
            "mirror_address_list": mirror_key_list,
            "LOG_LEVEL": serverGlobal.LOG_LEVEL,
            "READ_BUFF_SIZE": serverGlobal.READ_BUFF_SIZE,
            "SERVER_LISTEN": serverGlobal.SERVER_LISTEN,
            "MIRROR_LISTEN": serverGlobal.MIRROR_LISTEN,
        }
        return diyEncode(data)

    @staticmethod
    @route(URL_STINGER_SYNC, method='POST')
    def sync():
        # 获取webshell发送的数据
        serverGlobal.post_return_data = {}
        mirror_post_return_data = {}
        try:
            senddata = ControlCenter._get_post_data(request)
            # 获取数据错误
            if senddata is None:
                web_return_data = {ERROR_CODE: "Can not get data from post request"}
                return diyEncode(web_return_data)

            # 获取socks4a代理数据
            post_send_data = senddata.get(DATA_TAG)
            die_client_address = senddata.get(DIE_CLIENT_ADDRESS_TAG)

            # 获取mirror转发数据
            mirror_post_send_data = senddata.get(MIRROR_DATA_TAG)
            mirror_die_client_address = senddata.get(MIRROR_DIE_CLIENT_ADDRESS_TAG)
        except Exception as E:
            serverGlobal.logger.exception(E)
            serverGlobal.post_return_data = {ERROR_CODE: str(E)}
            return diyEncode(serverGlobal.post_return_data)

        serverGlobal.HAS_DATA = False
        # 处理die_client
        for client_address in die_client_address:
            try:
                one = serverGlobal.CHCHE_CONNS.pop(client_address)
                one.get("conn").close()
                serverGlobal.logger.info("CLIENT_ADDRESS:{} Close die_client_address ".format(client_address))
            except Exception as E:
                serverGlobal.logger.warning("CLIENT_ADDRESS:{} Close die_client_address error".format(client_address))

        for client_address in mirror_die_client_address:
            try:
                one = serverGlobal.MIRROR_CHCHE_CONNS.pop(client_address)
                one.get("conn").close()
                serverGlobal.logger.info("CLIENT_ADDRESS:{} Close mirror_die_client_address ".format(client_address))
            except Exception as E:
                serverGlobal.logger.warning(
                    "CLIENT_ADDRESS:{} Close mirror_die_client_address error".format(client_address))

        thread_list = []
        # 处理socks4a代理发送的数据
        for client_address in list(post_send_data.keys()):
            client_address_one_data = post_send_data.get(client_address)
            if serverGlobal.CHCHE_CONNS.get(client_address) is None:
                # 新建连接
                try:
                    server_socket_conn = socket.socket(AF_INET, SOCK_STREAM)
                    server_socket_conn.settimeout(serverGlobal.SOCKET_TIMEOUT)

                    target_ipaddress = client_address_one_data.get("targetaddr")[0]
                    target_port = int(client_address_one_data.get("targetaddr")[1])

                    server_socket_conn.connect((target_ipaddress, target_port), )  # json不支持元组,自动转化为list
                    serverGlobal.CHCHE_CONNS[client_address] = {"conn": server_socket_conn}

                    serverGlobal.logger.warning("CLIENT_ADDRESS:{} Create new tcp socket".format(client_address))
                except Exception as E:
                    serverGlobal.logger.warning(
                        "CLIENT_ADDRESS:{} TARGET_ADDR:{} Create new socket failed".format(client_address,
                                                                                           client_address_one_data.get(
                                                                                               "targetaddr"), E))
                    continue
            else:
                # 已有连接
                server_socket_conn = serverGlobal.CHCHE_CONNS.get(client_address).get("conn")

            # 读取数据
            try:
                tcp_send_data = base64.b64decode(client_address_one_data.get("data"))
            except Exception as E:
                serverGlobal.logger.exception(E)
                continue

            temp = Thread(target=handle_socks_data,
                          args=(server_socket_conn, tcp_send_data, client_address))
            thread_list.append(temp)

        for temp in thread_list:
            temp.start()
        for temp in thread_list:
            temp.join()

        # mirror
        # 处理client tcp接收的数据(mirror)
        for mirror_client_address in list(mirror_post_send_data.keys()):
            client_address_one_data = mirror_post_send_data.get(mirror_client_address)

            if serverGlobal.MIRROR_CHCHE_CONNS.get(mirror_client_address) is None:
                serverGlobal.logger.warning(
                    "MIRROR_CLIENT_ADDRESS:{} not in MIRROR_CHCHE_CONNS".format(mirror_client_address))
                continue
            else:
                server_socket_conn = serverGlobal.MIRROR_CHCHE_CONNS.get(mirror_client_address).get("conn")

            # 发送数据 tcp数据
            try:
                tcp_send_data = base64.b64decode(client_address_one_data.get("data"))
            except Exception as E:
                serverGlobal.logger.exception(E)
                continue

            send_flag = False
            for i in range(3):
                if tcp_send_data == '':
                    # 无数据发送跳出
                    send_flag = True
                    break
                try:
                    server_socket_conn.settimeout((i * 10 + 1) * serverGlobal.SOCKET_TIMEOUT)
                    server_socket_conn.sendall(tcp_send_data)
                    if len(tcp_send_data) > 0:
                        serverGlobal.logger.info(
                            "MIRROR_CLIENT_ADDRESS:{} CLIENT_TCP_SEND_LEN:{}".format(mirror_client_address,
                                                                                     len(tcp_send_data)))

                    send_flag = True
                    break
                except Exception as E:  # socket 已失效
                    serverGlobal.logger.warning(
                        "MIRROR_CLIENT_ADDRESS:{} Client send failed".format(mirror_client_address))
                    serverGlobal.logger.exception(E)

            if send_flag is not True:
                try:
                    server_socket_conn.close()
                    serverGlobal.MIRROR_CHCHE_CONNS.pop(mirror_client_address)
                except Exception as E:
                    serverGlobal.logger.exception(E)
                continue

        # 读取server tcp连接数据,存入post返回包中
        for mirror_client_address in list(serverGlobal.MIRROR_CHCHE_CONNS.keys()):
            server_socket_conn = serverGlobal.MIRROR_CHCHE_CONNS.get(mirror_client_address).get("conn")
            revc_flag = False
            for i in range(1):
                try:
                    tcp_recv_data = server_socket_conn.recv(serverGlobal.READ_BUFF_SIZE)
                    mirror_post_return_data[mirror_client_address] = {"data": base64.b64encode(tcp_recv_data)}
                    serverGlobal.logger.debug(
                        "MIRROR_CLIENT_ADDRESS:{} SERVER_TCP_RECV_DATA:{}".format(mirror_client_address, tcp_recv_data))
                    if len(tcp_recv_data) > 0:
                        serverGlobal.HAS_DATA = True
                        serverGlobal.logger.info(
                            "MIRROR_CLIENT_ADDRESS:{} SERVER_TCP_RECV_LEN:{}".format(mirror_client_address,
                                                                                     len(tcp_recv_data)))

                    revc_flag = True
                    break
                except Exception as err:
                    pass
            if revc_flag is not True:
                tcp_recv_data = b""
                mirror_post_return_data[mirror_client_address] = {"data": base64.b64encode(tcp_recv_data)}
                serverGlobal.logger.debug("TCP_RECV_NONE")

        serverGlobal.WAIT = 0
        if serverGlobal.HAS_DATA is True:
            serverGlobal.WAIT = 0
        else:
            if serverGlobal.WAIT >= 3:
                serverGlobal.WAIT = 3
            else:
                serverGlobal.WAIT += 0.05

        # 循环结束,返回web数据
        return_data = {
            RETURN_DATA: serverGlobal.post_return_data,
            MIRROR_RETURN_DATA: mirror_post_return_data,
            WAIT_TIME: serverGlobal.WAIT
        }
        return diyEncode(return_data)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            print(os.path.dirname(os.path.realpath(sys.argv[0])))
            sys.exit(1)
        listenip = sys.argv[1]
    else:
        listenip = LOCALADDR

    # 运行主控web服务
    SERVER_LISTEN = None
    for port in CONTROL_PORT:
        if port_is_used(port):
            continue
        else:
            SERVER_LISTEN = "{}:{}".format(LOCALADDR, port)
            break
    if SERVER_LISTEN is None:
        print("[x] There is no available control server port")
        sys.exit(1)

    MIRROR_LISTEN = None
    for port in MIRROR_PORT:
        if port_is_used(port):
            continue
        else:
            MIRROR_LISTEN = "{}:{}".format(listenip, port)
            break
    if MIRROR_LISTEN is None:
        print("[x] There is no available mirror server port")
        sys.exit(1)

    serverGlobal = ServerGlobal()
    serverGlobal.SERVER_LISTEN = SERVER_LISTEN
    serverGlobal.MIRROR_LISTEN = MIRROR_LISTEN

    serverGlobal.logger.info(
        "\nLOG_LEVEL: {}\n"
        "READ_BUFF_SIZE: {}\n"
        "SERVER_LISTEN: {}\n"
        "MIRROR_LISTEN: {}\n"
        "SOCKET_TIMEOUT: {}\n"
        "NO_LOG: {}\n".format(
            serverGlobal.LOG_LEVEL,
            serverGlobal.READ_BUFF_SIZE,
            serverGlobal.SERVER_LISTEN,
            serverGlobal.MIRROR_LISTEN,
            serverGlobal.SOCKET_TIMEOUT,
            serverGlobal.NO_LOG
        ))

    try:
        # 主控Web服务
        webthread = ControlCenter()
        webthread.setDaemon(True)
        webthread.start()
        # 反向mirror服务
        webserver = ThreadingTCPServer((MIRROR_LISTEN.split(":")[0], int(MIRROR_LISTEN.split(":")[1])),
                                       MirrorRequestHandler)
        serverGlobal.logger.warning("MirrorServer start on {}".format(MIRROR_LISTEN))
        webserver.serve_forever()
        serverGlobal.logger.warning("MirrorServer exit")

    except Exception as E:
        serverGlobal.logger.exception(E)
