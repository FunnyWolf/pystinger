# 毒刺(pystinger)
毒刺(pystinger)是一个通过webshell实现**内网端口转发出网&内网SOCK5代理出网**.工具主体使用python开发,当前支持php,jsp(x),aspx三种代理脚本.
# 使用方法
## 端口转发
* proxy.php上传到目标服务器,确保 [http://www.test.com/proxy.php](http://192.168.1.106:81/proxy.php)可以访问,页面返回 stinger XXX!
* 修改config.ini,示例如下(确保服务器127.0.0.1:8000,127.0.0.1:1080可以正常绑定)
```
[NET-CONFIG]
WEBSHELL = http://www.test.com/proxy.php
SERVER_LISTEN = 127.0.0.1:8000
TARGET_ADDR = 127.0.0.1:3389
LOCAL_ADDR = 127.0.0.1:33899

[TOOL-CONFIG]
LOG_LEVEL = INFO
READ_BUFF_SIZE = 10240
SLEEP_TIME = 0.0
```
* 将stinger_server.exe和config.ini上传到目标服务器同一目录,菜刀(蚁剑)执行mirror_server.exe启动服务端
* stinger_client和config.ini拷贝到本地PC的同一目录,命令行执行stinger_client,生成如下输出表示成功
```
2019-09-29 12:57:11,493 - INFO - 215 - Use SERVER_LISTEN as REMOTE_SERVER
2019-09-29 12:57:11,493 - INFO - 219 -  ------------Client Config------------
2019-09-29 12:57:11,493 - INFO - 222 - 
LOG_LEVEL: INFO
SLEEP_TIME:0.1
READ_BUFF_SIZE: 10240
WEBSHELL: http://192.168.3.10:82/proxy.php
REMOTE_SERVER: http://127.0.0.1:8000
LOCAL_ADDR: 127.0.0.1:33899


2019-09-29 12:57:11,500 - INFO - 63 -  ------------Server Config------------
2019-09-29 12:57:11,500 - INFO - 69 - 
LOG_LEVEL: INFO
READ_BUFF_SIZE: 10240
SERVER_LISTEN: 127.0.0.1:8000
TARGET_ADDR: 127.0.0.1:3389
client_address_list:[]
SOCK5: False
```
* 此时已经将192.168.3.10的3389端口映射到了你本地pc的33899端口
## SOCK5代理
* proxy.php上传到目标服务器,确保 [http://www.test.com/pro](http://192.168.1.106:81/proxy.php)[xy.](http://192.168.1.106:81/proxy.php)[php](http://192.168.1.106:81/proxy.php)可以访问,页面返回 stinger XXX!
* 修改config.ini,示例如下(确保服务器127.0.0.1:8000可以正常绑定)
```
[NET-CONFIG]
WEBSHELL = http://www.test.com/proxy.php
SERVER_LISTEN = 127.0.0.1:8000
TARGET_ADDR = 127.0.0.1:1080
LOCAL_ADDR = 127.0.0.1:10800

[TOOL-CONFIG]
LOG_LEVEL = INFO
READ_BUFF_SIZE = 10240
SLEEP_TIME = 0.01
[ADVANCED-CONFIG]
SOCKS5 = True
```
* 将stinger_server.exe和config.ini上传到目标服务器同一目录,菜刀(蚁剑)执行mirror_server.exe启动服务端
* stinger_client和config.ini拷贝到本地PC的同一目录,命令行执行stinger_client,生成如下输出表示成功
```
2019-09-29 13:03:41,164 - INFO - 215 - Use SERVER_LISTEN as REMOTE_SERVER
2019-09-29 13:03:41,164 - INFO - 219 -  ------------Client Config------------
2019-09-29 13:03:41,164 - INFO - 222 - 
LOG_LEVEL: INFO
SLEEP_TIME:0.1
READ_BUFF_SIZE: 10240
WEBSHELL: http://192.168.3.10:82/proxy.php
REMOTE_SERVER: http://127.0.0.1:8000
LOCAL_ADDR: 127.0.0.1:10800


2019-09-29 13:03:41,171 - INFO - 63 -  ------------Server Config------------
2019-09-29 13:03:41,171 - INFO - 69 - 
LOG_LEVEL: INFO
READ_BUFF_SIZE: 10240
SERVER_LISTEN: 127.0.0.1:8000
TARGET_ADDR: 127.0.0.1:1080
client_address_list:[]
SOCK5: True
2019-09-29 13:03:41,171 - INFO - 72 - Connet to server success
2019-09-29 13:03:41,173 - WARNING - 43 - LoopThread start
2019-09-29 13:03:41,173 - WARNING - 234 - Tcpserver start
```
* 此时已经你本地10800启动了一个192.168.3.10所在内网的socks5代理
# 相关工具
[https://github.com/nccgroup/ABPTTS](https://github.com/nccgroup/ABPTTS)
[https://github.com/sensepost/reGeorg](https://github.com/sensepost/reGeorg)
[https://github.com/SECFORCE/Tunna](https://github.com/SECFORCE/Tunna)
# 已测试
## stinger_server\stinger_client
* windows 
* linux
## proxy.jsp(x)/php/aspx
* php7.2 
* tomcat7.0 
* iis8.0
# 更新日志
**1.0**
更新时间: 2019-09-29
* 1.0正式版发布

