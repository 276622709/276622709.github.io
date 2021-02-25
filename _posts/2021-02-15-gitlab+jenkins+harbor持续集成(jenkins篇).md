---
layout: post
title: gitlab+jenkins+harbor持续集成(jenkins篇)
date: 2021-02-15
author: ZMY
header-img: ../img/2021-02-15/background.png
catalog : true
tags:
   - kubernetes
   - jenkins
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>gitlab+jenkins+harbor持续集成(jenkins篇)

**环境描述**

| 主机名/功能 | ip地址/访问方式               | 操作系统                      | 版本     | 备注   |
| ----------- | ----------------------------- | ----------------------------- | -------- | ------ |
| master      | 192.168.140.210               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node1       | 192.168.140.211               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node2       | 192.168.140.212               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| node3       | 192.168.140.213               | CentOS Linux release 7.4.1708 | v1.20.2  | 物理机 |
| gitlab      | http://192.168.140.212:10000  |                               | v13.8.2  | 容器   |
| jenkins     | http://192.168.140.212:29584/ |                               | v2.263.3 | 容器   |

官网文档[https://www.jenkins.io/doc/book/installing/kubernetes/](https://www.jenkins.io/doc/book/installing/kubernetes/)     

**jenkins安装过程**    

创建jenkins命名空间对资源进行隔离  

```
$ kubectl create namespace jenkins
```

列出命令空间  

```
$ kubectl get namespaces
```

编辑jenkins-deployment.yaml用于创建jenkins  
这里对官方文件修改了volumeMounts和securityContext对应值，为了之后使用docker in docker功能做准备

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts-jdk11
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
        - name: docker-socket
          mountPath: /var/run/docker.sock
        - name: docker-command
          mountPath: /usr/bin/docker
        securityContext:
          privileged: true
          runAsUser: 0
      volumes:
      - name: jenkins-home
        emptyDir: { }
      - name: docker-socket
        hostPath:
          path: /var/run/docker.sock
      - name: docker-command
        hostPath:
          path: /usr/bin/docker

```

部署jenkins

```
$ kubectl create -f jenkins-deployment.yaml -n jenkins
```

验证部署是否成功

```
$ kubectl get deployments -n jenkins
```

创建jenkins-service.yaml 用来暴露端口给外部访问，又名定义service

```
apiVersion: v1
kind: Service
metadata:
  name: jenkins
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    app: jenkins
```

创建service

```
$ kubectl create -f jenkins-service.yaml -n jenkins
```

验证部署service是否成功，观察映射的port，这里是32664，之后登陆jenkin控制台用

```
[root@node3 ~]# kubectl get services -n jenkins
NAME      TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
jenkins   NodePort   10.98.249.206   <none>        8080:29584/TCP   11s
```

查看jenkins pod名称，用来查看log

```
$ kubectl get pods -n jenkins
$ kubectl logs <pod_name> -n jenkins
```

日志内容如下，包括默认密码

>```
>
>*************************************************************
>*************************************************************
>*************************************************************
>
>Jenkins initial setup is required. An admin user has been created and a password generated.
>Please use the following password to proceed to installation:
>
>456b20d93bda48a7b4cea553fe198d43
>
>This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
>
>*************************************************************
>*************************************************************
>
>```

登陆jenkin控制台,用户名admin,密码是上面查看的密码

浏览器访问http://nodeip:29584

![](/img/2021-02-15/1.png)

登陆后界面如下，选择推荐的安装插件即可

![](/img/2021-02-15/2.png)

等待安装完成

![](/img/2021-02-15/3.png)

创建一个新的管理员账户，方便之后操作使用

![](/img/2021-02-15/4.png)

![](/img/2021-02-15/5.png)

首页展示如下

![](/img/2021-02-15/6.png)



**gitlab安装过程(略)**

gitlab配置过程请参考前一篇博客[gitlab+jenkins+harbor持续集成(gitlab篇)](https://276622709.github.io/2021/02/07/gitlab+jenkins+harbor%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90(gitlab%E7%AF%87)/)  

**gitlab配置过程**

这里配置gitlab webhook，并实现gitlab代码更新后，自动化部署的模拟过程

- 首先在gitlab上创建能够访问项目的jenkins用户

![](/img/2021-02-15/7.png)

![](/img/2021-02-15/8.png)

![](/img/2021-02-15/9.png)

修改密码

![](/img/2021-02-15/10.png)

![](/img/2021-02-15/11.png)

- 对项目的成员资格进行授权，这里对django_docker项目进行授权，授权给用户jenkins

![](/img/2021-02-15/12.png)

![](/img/2021-02-15/13.png)

- 配置gitlab服务器能够ssh免密码登陆到jenkins服务器上

登录到jenkins服务器，生成秘钥

```
jenkins@jenkins-585799558b-ksgs4:/$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/var/jenkins_home/.ssh/id_rsa): 
Created directory '/var/jenkins_home/.ssh'.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /var/jenkins_home/.ssh/id_rsa.
Your public key has been saved in /var/jenkins_home/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:cGyQKp4QcVhurHU1lFhRo3Khc49BQRnCE07/7qLqdSw jenkins@jenkins-585799558b-ksgs4
The key's randomart image is:
+---[RSA 2048]----+
|.+o.+*&Oo        |
|o+ o+*+* .       |
| .= *oB +        |
|.+...= O         |
|.o o  . S        |
|  o  . .         |
|    E o .        |
|   . o..         |
| .o... ..        |
+----[SHA256]-----+

```

将下面的秘钥复制到剪切板中

```
jenkins@jenkins-585799558b-ksgs4:/$ cat /var/jenkins_home/.ssh/id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vxo/SLr5kwuoNJbXaXI9296NvWOjSnR33CYRzrfs2G8ycQW++MfAELXF8xJNCw5geDJipPcj8+nn7xYiurKIbGrjnw2qpcnJCd8lOY1nVnqdo6k0SX+uXO6yPxcc+JG4q6SoQjm0+O683eUSZezqRo2YjunVUW3vEUC5zrFJ8nF8goNL6SLXW6iizlZPpu2YFkF30HSFXn9hdpC8WqPxSl34TROj9hFK2e1psEvlfXy7Bj0GNYitogAb5iYh4NsTcG7bUQPv1f2qZW7fMcvQrmLKnCHrdildyXJQApuWNc+bq1nDiflhsOO3BgpmohghrTcegqWheYA82hBcMK6L jenkins@jenkins-585799558b-ksgs4

```

gitlab上切换到jenkins用户后，添加ssh秘钥

![](/img/2021-02-15/14.png)

![](/img/2021-02-15/15.png)

- 创建tokens

![](/img/2021-02-15/16.png)

![](/img/2021-02-08/17.png)

复制tokens值(根据自己的实际情况来)，之后设置jenkin时会用到

>rho2cxLeUYsiik8oJseu

**jenkins配置过程**

通过web访问jenkins服务，添加gitlab插件  
gitlab插件的作用是能够使gitlab上的代码更新触发webhook进行jenkins的构建过程，并将结果反馈给gitlab

- 安装gitlab插件

![](/img/2021-02-15/18.png)

![](/img/2021-02-15/19.png)

- gitlab连接设置

![](/img/2021-02-15/20.png)

![](/img/2021-02-15/21.png)

token填写gitlab上面创建的token值

![](/img/2021-02-15/22.png)

设置git客户端连接用户名和email

![](/img/2021-02-15/23.png)

- 创建jenkins项目

![](/img/2021-02-15/24.png)

填写项目名称

![](/img/2021-02-15/25.png)

填写gitlab项目代码获取地址

![](/img/2021-02-15/26.png)

填写git clone代码时用的用户名和密码

![](/img/2021-02-15/27.png)

- 创建触发器

这里创建gitlab的webhook触发器，记录webhook的url，之后有用

![](/img/2021-02-15/28.png)

生成一个token，将这个值记录下来，之后在gitlab上填写webhook信息时候要用

![](/img/2021-02-15/29.png)

build设置shell脚本，模拟自动化流程，这里比较简单，模拟修改README.md文件后，查看内容是否有改变

![](/img/2021-02-15/30.png)

![](/img/2021-02-15/31.png)

- 登陆gitlab平台配置webhook

![](/img/2021-02-15/32.png)

填写web url网址和秘钥，并取消ssl验证

![](/img/2021-02-15/33.png)

报错如下，原因是不允许webhook和服务对本地网络进行请求

![](/img/2021-02-15/34.png)

对网络的外发请求进行配置

![](/img/2021-02-15/35.png)

![](/img/2021-02-15/36.png)

允许webhook和服务对本地网络进行请求

![](/img/2021-02-15/37.png)

![](/img/2021-02-15/38.png)

创建成功后，再次进行测试

![](/img/2021-02-15/39.png)

**模拟代码更新后，提交的代码能否自动触发jenkins流程并下载最近代码**

找一个具有git命令并能连接到gitlab的服务器，执行以下命令

```
# git clone http://192.168.140.212:10000/root/django_docker.git
# cd django_docker
# git config user.name jenkins
# git config user.email 2@2.com
# echo "ddd" >>  README.md
# git add .
# git commit -m "sdd"
# git push -u origin master
```

报如下错误，原因是gitlab默认对项目进行分支保护，只允许项目的创始人对项目进行代码的变更

>remote: GitLab: You are not allowed to push code to protected branches on this project.To http://192.168.140.212:10000/root/django_docker.git
> ! [remote rejected] master -> master (pre-receive hook declined)
>error: 无法推送一些引用到 'http://192.168.140.212:10000/root/django_docker.git'

关闭分支保护后，再次使用git push提交一次

![](/img/2021-02-15/40.png)

查看任务状态

![](/img/2021-02-15/41.png)

通过build history查看任务结果

![](/img/2021-02-15/42.png)

![](/img/2021-02-15/43.png)

可以看到代码进行了变化，并按照脚本进行执行，当然最终的目的是实现docker项目的自动更新，并更新docker镜像到harbor上，并可以自动部署到k8s生产环境，这些内容将在后面部署了harbor之后，[gitlab+jenkins+harbor持续集成(harbor篇)](https://276622709.github.io/2021/02/20/gitlab+jenkins+harbor%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90(harbor%E7%AF%87)/)中进行更新















声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。
