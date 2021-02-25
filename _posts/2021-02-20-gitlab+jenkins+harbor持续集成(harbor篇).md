---
layout: post
title: gitlab+jenkins+harbor持续集成(barbor篇)
date: 2021-02-20
author: ZMY
header-img: ../img/2021-02-20/background.png
catalog : true
tags:
   - kubernetes
   - harbor
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>gitlab+jenkins+harbor持续集成(harbor篇)

**环境描述**

| 主机名/功能 | ip地址/访问方式               | 操作系统                      | 版本     | 备注   |
| ----------- | ----------------------------- | ----------------------------- | -------- | ------ |
| master      | 192.168.140.210               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node1       | 192.168.140.211               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node2       | 192.168.140.212               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node3       | 192.168.140.213               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| gitlab      | http://192.168.140.212:10000  |                               | v13.8.2  | 容器   |
| jenkins     | http://192.168.140.212:29584/ |                               | v2.263.3 | 容器   |
| harbor      | http://192.168.140.210        |                               | v2.0.6   | 容器   |

前面2篇blog讲了gitlab进行代码上传后，触发jenkins自动化构建并执行自动化脚本过程

[gitlab+jenkins+harbor持续集成(gitlab篇)](http://)

[gitlab+jenkins+harbor持续集成(jenkins篇)](http://)

**harbor安装过程**

项目地址[https://github.com/goharbor/harbor/](https://github.com/goharbor/harbor/)

下载harbor最新tar包，有两种格式online和offline，我这里下载的是online

https://github.com/goharbor/harbor/releases

```
# tar xvf harbor-online-installer-v2.0.6.tgz 
# cd harbor
# cp harbor.yml.tmpl harbor.yml
```

修改barbor.tml文件参数，hostname和关闭https访问

```
# vim harbor.yml
```

```
hostname: 192.168.140.210
#https:
  # https port for harbor, default is 443
#  port: 443
  # The path of cert and key files for nginx
#  certificate: /your/certificate/path
#  private_key: /your/private/key/path

```

执行install.sh脚本

```
sh install.sh
```

由于harbor没有开启加密传输，故需要对docker客户端修改/etc/docker/daemon.json  

对于我的环境来说就是master,node1,node2,node3上修改

```
{
"insecure-registries" : ["192.168.140.210"]
}
```

重启docker服务

```
# systemctl restart docker
```

完全删除harbor相关容器

```
# docker-compose down -v
```

创建(若没有)启动harbor容器

```
docker-compose up -d
```

web访问http://192.168.140.210  

默认用户名:admin密码:Harbor12345  

首页如下

![](/img/2021-02-20/1.png)

创建用来存储image的项目

![](/img/2021-02-20/2.png)

![](/img/2021-02-20/3.png)

**部署难点**

由于jenkins容器中需要完成docker build、docker push等操作，默认jenkins容器中不含有docker命令  
有俩种解决办法,第一种在jenkins容器中直接安装docker环境，操作了一遍后发现修改daemon.json后docker服务无法重启，无法使"insecure-registries" : ["192.168.140.210:5000"]生效，因此采用了第二种方法即将docker的socket和docker命令在jenkins启动时挂载到jenkins里，并且在yml文件中添加privilege和runasroot权限，过程请参考[gitlab+jenkins+harbor持续集成(jenkins篇)](http://)中jenkins-deployment.yaml文件内容，这里不再复述

登陆jenkins平台，找到之前创建的test项目修改jenkins的build过程中shell脚本内容

![](/img/2021-02-20/4.png)

```
cd $WORKSPACE
time=`date +%s`
version=`cat Versions`
docker build -t $time .
docker tag $time 192.168.140.210/newapp/myapp:$version
docker login -u admin -p Harbor12345
docker push 192.168.140.210/newapp/myapp:$version
docker rmi $time
docker rmi 192.168.140.210/newapp/myapp:$version
```

点击立即执行

![](/img/2021-02-20/5.png)

观察返回结果，成功显示:success

![](/img/2021-02-20/6.png)

查看harbor上是否有镜像文件生成

![](/img/2021-02-20/7.png)

对镜像内容进行验证,我这里再node1上进行镜像的验证

```
[root@node1 ~]# docker pull 192.168.140.210/newapp/myapp:v1.0
[root@node1 ~]# docker run -d -p 20000:20000 192.168.140.210/newapp/myapp:v1.0
758d0baa43211783b5f3f5ce0ec233ee11a64a5d8f08d9d1cef765b701a34576
```

网页访问http://192.168.140.211:20000, 命令行中输入df -h

![](/img/2021-02-20/8.png)

修改git项目内容将index.html中ifconfig--->date  

修改Versions文件内容v1.0--->v1.1

git客户端提交  

```
#git add .
#git commit -m "."
#git push -u origin master
```

查看jenkins能否自动构建docker镜像，并上传到harbor上  

![](/img/2021-02-20/10.png)

上面可以看到v1.1版本镜像已经成功上传到harbor，接下来通过这个进行进行验证

```
[root@node1 ~]# docker pull 192.168.140.210/newapp/myapp:v1.1
[root@node1 ~]# docker run -d -p 20001:20000 192.168.140.210/newapp/myapp:v1.1
```

网页访问http://192.168.140.211:20001,查看结果

![](/img/2021-02-20/9.png)

通过如上操作步骤完成了gitlab+jenkins+harbor的持续集成项目的全部过程，对于gitlab和jenkins的安装和部署

gitlab安装过程，请参考上一篇博客[]()

jenkins安装及配置过程，请参考上一篇博客[]()





声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。