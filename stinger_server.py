# -*- coding: utf-8 -*-
# @File  : server.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf 
# @Author: funnywolf
# @Contact : github.com/FunnyWolf

########### only for python2.7 because pyinstaller
# import twisted

from socket import AF_INET, SOCK_STREAM

from bottle import request, route, run as bottle_run

from config import *

global serverGlobal


class ServerGlobal(object):
    def __init__(self):
        self.CHCHE_CONNS = {}
        self.READ_BUFF_SIZE = BUFSIZE
        self.SOCKET_TIMEOUT = DEFAULT_SOCKET_TIMEOUT
        self.LOG_LEVEL = "INFO"
        self.NO_LOG = True
        if self.NO_LOG:
            self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
        else:
            self.logger = get_logger(level=self.LOG_LEVEL, name="FileLogger")

        self.SERVER_LISTEN = None

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
                self.logger = get_logger(level=self.LOG_LEVEL, name="FileLogger")
        elif tag == "NO_LOG":
            if self.NO_LOG:
                self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")
            else:
                self.logger = get_logger(level=self.LOG_LEVEL, name="FileLogger")
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
                    one.get("conn").close()
                serverGlobal.logger.info("Clean exist sockets")
                return True
            except Exception as E:
                serverGlobal.logger.exception(E)
                return False


class ControlCenter(object):

    def __init__(self, ):
        pass

    def run(self):
        serverGlobal.logger.warning("WebServer start on {}".format(serverGlobal.SERVER_LISTEN))
        bottle_run(host=serverGlobal.SERVER_LISTEN.split(":")[0],
                   port=int(serverGlobal.SERVER_LISTEN.split(":")[1]),
                   quiet=True,
                   server='twisted'
                   )
        serverGlobal.logger.warning("WebServer exit")

    @staticmethod
    def _get_post_data(request):
        try:
            unformat_SENDDATA = request.forms.get("SENDDATA")
            serverGlobal.logger.debug(unformat_SENDDATA)
            senddata = newLoads(unformat_SENDDATA)
        except Exception as E:
            serverGlobal.logger.exception(E)
            return None
        return senddata

    @staticmethod
    @route('/')
    def index():
        return '<b>Hello stinger</b>!'

    @staticmethod
    @route(URL_SET_CONFIG, method='POST')
    def set_config():
        """参数设置函数"""
        try:
            senddata = ControlCenter._get_post_data(request)
            tag = senddata.get(CONFIG_TAG)
            data = senddata.get(CONFIG_DATA)
            result = serverGlobal.set(tag, data)
            return newDumps(result)
        except Exception as E:
            serverGlobal.logger.exception(E)
            web_return_data = {ERROR_CODE: str(E)}
            return newDumps(web_return_data)

    @staticmethod
    @route(URL_CMD, method='POST')
    def run_cmd():
        """命令执行函数"""
        try:
            senddata = ControlCenter._get_post_data(request)
            tag = senddata.get(CONFIG_TAG)
            data = senddata.get(CONFIG_DATA)
            result = serverGlobal.cmd(tag, data)
            return newDumps(result)
        except Exception as E:
            serverGlobal.logger.exception(E)
            web_return_data = {ERROR_CODE: str(E)}
            return newDumps(web_return_data)

    @staticmethod
    @route(URL_CHECK, method='POST')
    def check():
        """自检函数"""
        serverGlobal.logger.debug("CHCHE_CONNS : {}".format(len(serverGlobal.CHCHE_CONNS)))
        # 返回现有连接
        key_list = []
        for key in serverGlobal.CHCHE_CONNS:
            key_list.append(key)
        data = {
            "client_address_list": key_list,
            "LOG_LEVEL": serverGlobal.LOG_LEVEL,
            "READ_BUFF_SIZE": serverGlobal.READ_BUFF_SIZE,
            "SERVER_LISTEN": serverGlobal.SERVER_LISTEN,

        }
        return newDumps(data)

    @staticmethod
    @route(URL_STINGER_SYNC, method='POST')
    def sync():
        # 获取webshell发送的数据
        post_return_data = {}
        try:
            senddata = ControlCenter._get_post_data(request)
            post_send_data = senddata.get(DATA_TAG)
            die_client_address = senddata.get(DIE_CLIENT_ADDRESS_TAG)
        except Exception as E:
            serverGlobal.logger.exception(E)
            post_return_data = {ERROR_CODE: str(E)}
            return newDumps(post_return_data)

        # 处理die_client
        for client_address in die_client_address:
            try:
                one = serverGlobal.CHCHE_CONNS.pop(client_address)
                one.get("conn").close()
                serverGlobal.logger.warning("CLIENT_ADDRESS:{} Close die_client_address ".format(client_address))
            except Exception as E:
                serverGlobal.logger.warning("CLIENT_ADDRESS:{} Close die_client_address error".format(client_address))

        # 处理tcp发送的数据
        for client_address in list(post_send_data.keys()):
            client_address_one_data = post_send_data.get(client_address)

            if serverGlobal.CHCHE_CONNS.get(client_address) is None:
                # 新建链接
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
                server_socket_conn = serverGlobal.CHCHE_CONNS.get(client_address).get("conn")

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
                continue

            # 读取数据 tcp数据
            revc_flag = False
            for i in range(1):
                try:
                    # server_socket_conn.settimeout((i*3+1)*serverGlobal.SOCKET_TIMEOUT)
                    tcp_recv_data = server_socket_conn.recv(serverGlobal.READ_BUFF_SIZE)
                    post_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
                    serverGlobal.logger.debug(
                        "CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(client_address, tcp_recv_data))
                    if len(tcp_recv_data) > 0:
                        serverGlobal.logger.info(
                            "CLIENT_ADDRESS:{} TCP_RECV_LEN:{}".format(client_address, len(tcp_recv_data)))
                    revc_flag = True
                    break
                except Exception as err:
                    pass
            if revc_flag is not True:
                tcp_recv_data = b""
                post_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
                serverGlobal.logger.debug("TCP_RECV_NONE")

        # 循环结束,返回web数据
        return newDumps(post_return_data)


if __name__ == '__main__':

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
        exit(1)

    serverGlobal = ServerGlobal()
    serverGlobal.SERVER_LISTEN = SERVER_LISTEN

    serverGlobal.logger.info(
        "\nLOG_LEVEL: {}\n"
        "READ_BUFF_SIZE: {}\n"
        "SERVER_LISTEN: {}\n"
        "SOCKET_TIMEOUT: {}\n"
        "NO_LOG: {}\n".format(
            serverGlobal.LOG_LEVEL,
            serverGlobal.READ_BUFF_SIZE,
            serverGlobal.SERVER_LISTEN,
            serverGlobal.SOCKET_TIMEOUT,
            serverGlobal.NO_LOG
        ))
    try:
        # 主控Web服务
        webthread = ControlCenter()
        webthread.run()
    except Exception as E:
        serverGlobal.logger.exception(E)
