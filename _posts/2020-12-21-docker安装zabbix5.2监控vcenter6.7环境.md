---
layout: post
title: 使用docker安装zabbix5.2监控vcenter6.7环境
date: 2020-12-21
author: ZMY
header-img: ../img/monitor_alarm_background.jpg
catalog : true
tags:
    - zabbix
    - docker  
typora-root-url: ..
---

## <img class="original" src='/img/original.png'> 使用docker安装zabbix5.2监控vcenter6.7环境

## 目的

现在驻场的地方使用的虚拟化平台是vcenter6.7环境，因此急需一个监控平台去及时发现问题，方便运维管理

在开源解决方案里，zabbix是一个不错的选择。并且随着docker的发展越来越迅速，很多开源软件都提供了

docker的安装方式，故这次选择docker安装zabbix5.2环境用来监控vcenter6.7环境

## 环境描述

**物理环境:**

3台服务器组成的vsphere6.7环境，其中一台服务器上的一台虚拟机搭建了vcenter6.7 appliance,并且3台服务器组成了vsan集群

**zabbix安装环境:**

一台centos7.4x64虚拟机用来安装基于docker的zabbix

## 安装过程

1.安装docker环境

- 替换yum源

```
# cd /etc/yum.repos.d/
# mkdir repo_bak
# mv *.repo repo_bak/
# wget http://mirrors.aliyun.com/repo/Centos-7.repo
# yum install epel-release -y
```

- 安装docker引擎和docker-compose

```
# yum install -y yum-utils git
# sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
# yum install docker-ce docker-ce-cli containerd.io -y
# yum install gcc python-devel python3 -y
# pip3 install docker-compose
```

- 启动docker服务并设置开机自启动  

```
# systemctl start docker
# systemctl enable docker
```

2.安装docker-zabbix  

```
# git clone https://github.com/zabbix/zabbix-docker.git
# cd zabbix-docker
# vim docker-compose_v3_centos_mysql_latest.yaml
```

将zabbix-proxy-sqlite3，zabbix-web-nginx-mysql，zabbix-agent 这3个容器注释掉后使用docker-compose创建容器  

```
# docker-compose -f docker-compose_v3_centos_mysql_latest.yaml up -d
```

修改.env_srv文件中ZBX_STARTVMWARECOLLECTORS变量,否者docker启动不会加载vmware模块  

```
ZBX_STARTVMWARECOLLECTORS=5
```

使用docker-compose 重启docker-zabbix  

```
# docker-compose -f docker-compose_v3_centos_mysql_latest.yaml kill
# docker-compose -f docker-compose_v3_centos_mysql_latest.yaml up -d
```

官网说明文档[https://www.zabbix.com/documentation/current/manual/installation/containers](https://www.zabbix.com/documentation/current/manual/installation/containers)

3.修改vcenter中参数值

config.vpxd.stats.maxQueryMetrics 修改成256

默认没有config.vpxd.stats.maxQueryMetrics参数，需要手动添加。

![](/img/2020-12-21/1.png)

官网说明文档[https://kb.vmware.com/s/article/2107096](https://kb.vmware.com/s/article/2107096)

## zabbix平台配置过程

1.登陆zabbix，添加vcenter环境  

通过浏览器即可访问zabbix http://ip  ,默认用户名Admin,密码zabbix      

登陆后先进行偏好设置，将语言调成中文，时间调成shanghai,主题选个自己喜欢的就好      

![](/img/2020-12-21/2.png)

首页如下图所示，现在只有一个本机的10051zabbix服务端口在监控  

![](/img/2020-12-21/3.png)

2.添加vcenter平台监控信息，获取监控数据  

- 找到macros模板，将vcenter相关信息添加进去  

  ![](/img/2020-12-21/4.png)

  ![](/img/2020-12-21/5.png)将你的vcenter信息添加进去，有时间的话最好在vcenter上建一个专门用来监控的账号，我这里就不展示了  

  ![](/img/2020-12-21/6.png)

- 创建主机，起个主机名，主机组名，关联macros模板  

  ![](/img/2020-12-21/7.png)

  ![](/img/2020-12-21/7_5.png)

  ![](/img/2020-12-21/8.png)

- 添加完成，默认一个小时后出现数据  

  ![](/img/2020-12-21/12.png)

- 通过最新数据观察是否有数据产生(有些数据需要一个小时候才能发现)  

  ![](/img/2020-12-21/13.png)

参考资料[https://bestmonitoringtools.com/vmware-monitoring-with-zabbix-esxi-vcenter-vm-vsphere/](https://bestmonitoringtools.com/vmware-monitoring-with-zabbix-esxi-vcenter-vm-vsphere/)

3.创建触发器

- 在模板中找到VMware模板  

![](/img/2020-12-21/14.png)

- 点击Discover VMware Datastores 对应的触发器类型  

![](/img/2020-12-21/15.png)

- 点击创建触发器类型  

![](/img/2020-12-21/16.png)

- 创建触发器触发条件  

![](/img/2020-12-21/17.png)

为了观察效果，你可以调整数值，但是一个小时之后才能看到触发器触发的问题  

4.添加图形展示  

- 前几步和3里的添加触发器类型一样，这里选择模板VMware下Discover Vmware Datastores的图形原型

![](/img/2020-12-21/18.png)

- 创建图形原型

![](/img/2020-12-21/19.png)

- 添加名称，将查看触发器勾掉

![](/img/2020-12-21/20.png)

- 添加监控项原型的值

![](/img/2020-12-21/21.png)

最后别忘了点击添加按钮,图形生产也是1个小时之后  

这里只是添加了一个简单数据存储读写延迟的图形化展示，并且看起来不太炫酷，下一篇博客会展示如何通过  granafa+telegraf+influxdb的形式监控vcenter6.7环境 (有国外大神已经做好了相应的模板，可以直接调用)    



5.添加报警

参考之前写的[blog](https://276622709.github.io/2018/10/21/zabbix4.0%E5%88%9D%E4%BD%93%E9%AA%8C/)将zabbix报警通过微信接收,这里略  





声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。