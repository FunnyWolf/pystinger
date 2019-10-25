# -*- coding: utf-8 -*-
# @File  : server.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf 
# @Author: funnywolf
# @Contact : github.com/FunnyWolf
########### only for python2.7 because pyinst
try:
    from socketserver import BaseRequestHandler
    from socketserver import ThreadingTCPServer
    from socketserver import StreamRequestHandler
    import configparser as conp
except Exception as E:
    from SocketServer import BaseRequestHandler
    from SocketServer import ThreadingTCPServer
    from SocketServer import StreamRequestHandler
    import ConfigParser as conp

import json
import os
import select
import socket
import struct
import sys
from socket import AF_INET, SOCK_STREAM
from threading import Thread

from bottle import request
from bottle import route
from bottle import run as bottle_run

from config import *

global cache_conns, server_die_client_address
global READ_BUFF_SIZE, LOG_LEVEL, SERVER_LISTEN, TARGET_ADDR, SOCKS5, SOCKET_TIMEOUT


# import SocketServer
# class ThreadingTCPServerReuse(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#     allow_reuse_address = True

class Socks5Server(StreamRequestHandler):
    @staticmethod
    def send_all(sock, data):
        bytes_sent = 0
        while True:
            r = sock.send(data[bytes_sent:])
            if r < 0:
                return r
            bytes_sent += r
            if bytes_sent == len(data):
                return bytes_sent

    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            while True:
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = sock.recv(4096)
                    if len(data) <= 0:
                        break

                    result = Socks5Server.send_all(remote, data)
                    if result < len(data):
                        raise Exception('failed to send all data')

                if remote in r:
                    data = remote.recv(4096)
                    if len(data) <= 0:
                        break

                    result = Socks5Server.send_all(sock, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
        finally:
            sock.close()
            remote.close()

    def handle(self):
        try:
            sock = self.connection
            sock.recv(262)
            sock.send("\x05\x00")
            data = self.rfile.read(4) or '\x00' * 4
            mode = ord(data[1])
            if mode != 1:
                logger.warn('mode != 1')
                return

            addrtype = ord(data[3])
            if addrtype == 1:
                addr_ip = self.rfile.read(4)
                addr = socket.inet_ntoa(addr_ip)
            elif addrtype == 3:
                addr_len = self.rfile.read(1)
                addr = self.rfile.read(ord(addr_len))
            elif addrtype == 4:
                addr_ip = self.rfile.read(16)
                addr = socket.inet_ntop(socket.AF_INET6, addr_ip)
            else:
                logger.warn('addr_type not support')
                # not support
                return
            addr_port = self.rfile.read(2)
            port = struct.unpack('>H', addr_port)
            try:
                reply = "\x05\x00\x00\x01"
                reply += socket.inet_aton('0.0.0.0') + struct.pack(">H", 2222)
                self.wfile.write(reply)
                # reply immediately
                remote = socket.create_connection((addr, port[0]))
                logger.info('connecting %s:%d' % (addr, port[0]))
            except socket.error as e:
                logger.warn(e)
                return
            self.handle_tcp(sock, remote)
        except socket.error as e:
            logger.warn(e)


class WebThread(Thread):  # 继承父类threading.Thread
    def __init__(self, ):
        Thread.__init__(self)

    def run(self):
        logger.warning("WebServer start on {}".format(SERVER_LISTEN))
        bottle_run(host=SERVER_LISTEN.split(":")[0], port=int(SERVER_LISTEN.split(":")[1]), quiet=True)
        logger.warning("WebServer exit")

    @staticmethod
    @route('/check/', method='POST')
    def check():
        """自检函数"""
        logger.debug("cache_conns : {}".format(len(cache_conns)))
        # 返回现有连接
        key_list = []
        for key in cache_conns:
            key_list.append(key)
        data = {
            "client_address_list": key_list,
            "LOG_LEVEL": LOG_LEVEL,
            "READ_BUFF_SIZE": READ_BUFF_SIZE,
            "SERVER_LISTEN": SERVER_LISTEN,
            "TARGET_ADDR": TARGET_ADDR,
            "SOCKS5": SOCKS5,
        }
        return b64encodeX(json.dumps(data).encode("utf-8"))

    @staticmethod
    @route('/stinger_sync/', method='POST')
    def sync():
        web_return_data = {}
        unformat_DATA = request.forms.get("DATA")
        unformat_Die_client_address = request.forms.get("Die_client_address")
        try:
            data = json.loads(b64decodeX(unformat_DATA))
            die_client_address = json.loads(b64decodeX(unformat_Die_client_address))
        except Exception as E:
            logger.exception(E)
            logger.error(unformat_DATA)
            logger.error(unformat_Die_client_address)
            tcp_recv_data = WRONG_DATA
            return b64encodeX(tcp_recv_data)

        for client_address in die_client_address:
            try:
                one = cache_conns.pop(client_address)
                one.get("conn").close()
                logger.warning("CLIENT_ADDRESS:{} Close die_client_address ".format(client_address))
            except Exception as E:
                logger.warning("CLIENT_ADDRESS:{} Close die_client_address error".format(client_address))
                logger.exception(E)

        for client_address in list(data.keys()):
            if cache_conns.get(client_address) is None:
                # 新建链接
                try:
                    client = socket.socket(AF_INET, SOCK_STREAM)
                    client.settimeout(SOCKET_TIMEOUT)
                    client.connect((TARGET_ADDR.split(":")[0], int(TARGET_ADDR.split(":")[1])))
                    logger.warning("CLIENT_ADDRESS:{} Create new tcp socket".format(client_address))
                    cache_conns[client_address] = {"conn": client}
                except Exception as E:
                    logger.warning(
                        "CLIENT_ADDRESS:{} TARGET_ADDR:{} Create new socket failed".format(client_address, TARGET_ADDR))
                    continue
            else:
                client = cache_conns.get(client_address).get("conn")

            tcp_send_data = base64.b64decode(data.get(client_address).get("data"))

            send_flag = False
            for i in range(20):
                # 发送数据
                try:
                    client.sendall(tcp_send_data)
                    logger.info("CLIENT_ADDRESS:{} TCP_SEND_LEN:{}".format(client_address, len(tcp_send_data)))
                    send_flag = True
                    break
                except Exception as E:  # socket 已失效
                    logger.warning("CLIENT_ADDRESS:{} Client send failed".format(client_address))
                    logger.exception(E)

            if send_flag is not True:
                try:
                    client.close()
                    cache_conns.pop(client_address)
                except Exception as E:
                    logger.exception(E)
                continue

            revc_flag = False
            for i in range(3):
                # 读取数据
                try:
                    tcp_recv_data = client.recv(READ_BUFF_SIZE)
                    web_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
                    logger.debug("CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(client_address, tcp_recv_data))
                    if len(tcp_recv_data) > 0:
                        logger.info("CLIENT_ADDRESS:{} TCP_RECV_LEN:{}".format(client_address, len(tcp_recv_data)))
                    revc_flag = True
                    break
                except Exception as err:
                    pass
            if revc_flag is not True:
                tcp_recv_data = b""
                web_return_data[client_address] = {"data": base64.b64encode(tcp_recv_data)}
                logger.debug("TCP_RECV_NONE")

        # 循环结束,返回web数据
        return b64encodeX(json.dumps(web_return_data))


if __name__ == '__main__':

    if os.path.exists('config.ini') is not True:
        print("Please copy config.ini into same folder!")
        sys.exit(1)
    configini = conp.ConfigParser()
    configini.read("config.ini")
    # 设置日志级别
    try:
        LOG_LEVEL = configini.get("TOOL-CONFIG", "LOG_LEVEL")
    except Exception as E:
        LOG_LEVEL = "INFO"
    try:
        no_log_flag = configini.get("ADVANCED-CONFIG", "NO_LOG")
        if no_log_flag.lower() == "true":
            logger = get_logger(level=LOG_LEVEL, name="StreamLogger")
        else:
            logger = get_logger(level=LOG_LEVEL, name="FileLogger")
    except Exception as E:
        logger = get_logger(level=LOG_LEVEL, name="FileLogger")
    # read_buff_size
    try:
        READ_BUFF_SIZE = int(configini.get("TOOL-CONFIG", "READ_BUFF_SIZE"))
    except Exception as E:
        logger.exception(E)
        READ_BUFF_SIZE = 10240

    try:
        socks5_on = configini.get("ADVANCED-CONFIG", "SOCKS5")
        if socks5_on.lower() == "true":
            SOCKS5 = True
        else:
            SOCKS5 = False
    except Exception as E:
        SOCKS5 = False

    # socket_timeout
    try:
        SOCKET_TIMEOUT = float(configini.get("TOOL-CONFIG", "SOCKET_TIMEOUT"))
    except Exception as E:
        SOCKET_TIMEOUT = 0.1

    # socks5
    try:
        socks5_on = configini.get("ADVANCED-CONFIG", "SOCKS5")
        if socks5_on.lower() == "true":
            SOCKS5 = True
        else:
            SOCKS5 = False
    except Exception as E:
        SOCKS5 = False

    # 获取核心参数
    try:
        SERVER_LISTEN = configini.get("NET-CONFIG", "SERVER_LISTEN")
        TARGET_ADDR = configini.get("NET-CONFIG", "TARGET_ADDR")
    except Exception as E:
        logger.exception(E)
        sys.exit(1)

    logger.info(
        "\nLOG_LEVEL: {}\nREAD_BUFF_SIZE: {}\nSERVER_LISTEN: {}\nTARGET_ADDR: {}\nSOCKS5: {}\nSOCKET_TIMEOUT: {}\n".format(
            LOG_LEVEL, READ_BUFF_SIZE, SERVER_LISTEN, TARGET_ADDR, SOCKS5, SOCKET_TIMEOUT
        ))

    cache_conns = {}
    server_die_client_address = []
    # socks5方式启动
    if SOCKS5:
        try:
            webthread = WebThread()
            webthread.setDaemon(True)
            webthread.start()
            # socks5服务
            server = ThreadingTCPServer((TARGET_ADDR.split(":")[0], int(TARGET_ADDR.split(":")[1])), Socks5Server)
            logger.warning("Socks5Server start on {}".format(TARGET_ADDR))
            server.serve_forever()
            # webthread.join()
        except Exception as E:
            logger.exception(E)
    else:
        try:
            webthread = WebThread()
            webthread.start()
            # webthread.join()
        except Exception as E:
            logger.exception(E)
