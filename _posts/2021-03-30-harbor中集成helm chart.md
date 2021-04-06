---
layout: post
title: harbor集成helm charts
date: 2021-03-30
author: ZMY
header-img: ../img/2021-03-30/background.png
catalog : true
tags:
   - helm charts
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>harbor集成helm charts

| 主机名/功能 | ip地址/访问方式        | 操作系统                      | 版本    | 备注   |
| ----------- | ---------------------- | ----------------------------- | ------- | ------ |
| master      | 192.168.140.210        | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node1       | 192.168.140.211        | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node2       | 192.168.140.212        | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node3       | 192.168.140.213        | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| harbor      | http://192.168.140.212 |                               | v2.0    | 容器   |

harbor集成helm charts官网地址[https://goharbor.io/docs/1.10/working-with-projects/working-with-images/managing-helm-charts/](https://goharbor.io/docs/1.10/working-with-projects/working-with-images/managing-helm-charts/)



**背景**

已完成k8s环境和harbor的搭建与部署，在harbor环境中部署helm charts功能，完善k8s环境部署应用功能

**helm charts优势**

​    1.方便快捷

​     不需要寻找yaml资源，尤其有的pod包括service资源、serviceaccount、rbac、volume等等需要多个yaml文件

​    2.版本管理

​    可以升级和降级到指定版本

​    3.变量修改方便

​    根据用户不同需求更改参数变量，完成自定义安装

**helm目录结构**

myapp

​    -charts/

​    -Chart.yaml

​    -templates/

​        -NOTES.txt

​        -*.yaml

​    -values.yaml

若想查看每个文件的作用及参数的解释可参考官网文档[https://helm.sh/docs/topics/charts/](https://helm.sh/docs/topics/charts/)



**harbor集成helm charts操作流程**

1.使用之前实验环境进行操作，对harbor进行charts插件安装，harbor部署参考之前的blog[gitlab+jenkins+harbor持续集成(harbor篇)](https://276622709.github.io/2021/02/20/gitlab+jenkins+harbor%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90(harbor%E7%AF%87)/)

```
# docker-compose down
# ./install.sh --with-chartmuseum
```

2.登陆harbor平台，为helm repo创建一个项目项目名为helm-repo，并设置为可公开访问

![](/img/2021-03-30/1.png)

两种方式上传charts包到helm charts库中

1)直接网页upload上传tar包

![](/img/2021-03-30/2.png)

2)helm push命令上传
最新安装包下载地址https://github.com/helm/helm/releases
为了方便之后使用chart在k8s上部署容器，我选择第二种方式进行charts包的上传
客户端下载helm并安装

```
# wget https://get.helm.sh/helm-v3.5.3-linux-amd64.tar.gz
# tar xvf helm-v3.5.3-linux-amd64.tar.gz
# cd helm && mv helm /usr/local/bin/
# helm plugin install https://github.com/chartmuseum/helm-push
```

3.添加harbor的repo库到客户端

```
[root@master ~]# helm repo add --username=admin --password=Harbor12345 harbor_repo http://192.168.140.210/chartrepo/helm-repo
"harbor_repo" has been added to your repositories
```

4.创建一个charts

```
# helm create myapp && cd myapp
# vim values.yaml
```

修改的内容如下

```
service:
#  type: ClusterIP
  type: NodePort
#  port: 80
  port: 80
  targetPort: 80
  nodePort: 30080
```

为了访问时使用节点的固定端口访问,修改templates/service.yaml,添加一行nodePort 

```
nodePort: {{ .Values.service.nodePort}}
```

5.修改后使用helm lint检查语法是否有错误

```
[root@master myapp]# helm lint --strict
==> Linting .
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

6.进行本地测试debug查看各个参数数值

```
helm install . --dry-run --debug ./myapp
```

7.对charts进行打包

```
# helm package .
```

8.对发布的charts包进行上传，上传到之前创建的harbor_repo库中

```
# helm push myapp-0.1.0.tgz harbor_repo
```

9.进行部署前对repo库进行更新

```
# helm repo update
```

10.列出安装包信息

```
[root@master myapp]# helm search repo
NAME             	CHART VERSION	APP VERSION	DESCRIPTION                
harbor_repo/myapp	0.1.0        	1.16.0     	A Helm chart for Kubernetes
```

11.接下来开始安装这个charts，首先创建一个独立的namespace

```
# kubectl create namespace nginx-test
```

12.helm命令安装charts

```
# helm install nginx-zhai harbor_repo/myapp --namespace nginx-test
```

13.访问节点的30080端口查看通过安装chart的方式部署的nginx程序是否成功

![](/img/2021-03-30/3.png)



**helm chart的升级和回滚**

1.将nodePort从30080变为30090

```
service:
  type: NodePort
  port: 80
  targetPort: 80
  nodePort: 30090
```

2.将Chart.yaml中的版本信息修改一下

```
version: 0.2.0
appVersion: "1.17.0"
```

3.重新打包并上传

```
# helm package .
# helm push myapp-0.2.0.tgz harbor_repo
```

4.对repo库进行更新

```
# helm repo update
```

5.查看所有版本

```
[root@master myapp]# helm search repo -l
NAME             	CHART VERSION	APP VERSION	DESCRIPTION                
harbor_repo/myapp	0.2.0        	1.17.0     	A Helm chart for Kubernetes
harbor_repo/myapp	0.1.0        	1.16.0     	A Helm chart for Kubernetes
```

6.对nginx应用进行版本升级

```
# helm upgrade nginx-zhai harbor_repo/myapp -n nginx-test
```

7.查看版本历史

```
[root@master myapp]# helm history nginx-zhai -n nginx-test
REVISION	UPDATED                 	STATUS    	CHART      	APP VERSION	DESCRIPTION     
1       	Tue Apr  6 15:25:14 2021	superseded	myapp-0.1.0	1.16.0     	Install complete
2       	Tue Apr  6 16:22:07 2021	deployed  	myapp-0.2.0	1.17.0     	Upgrade complete
```

8.访问网页看端口是否更改成功

![](/img/2021-03-30/4.png)

9.对应用进行版本回滚

```
# helm rollback nginx-zhai 1 -n nginx-test
```

10.再次查看版本历史

```
[root@master myapp]# helm history nginx-zhai -n nginx-test
REVISION	UPDATED                 	STATUS    	CHART      	APP VERSION	DESCRIPTION     
1       	Tue Apr  6 15:25:14 2021	superseded	myapp-0.1.0	1.16.0     	Install complete
2       	Tue Apr  6 16:22:07 2021	superseded	myapp-0.2.0	1.17.0     	Upgrade complete
3       	Tue Apr  6 16:25:53 2021	deployed  	myapp-0.1.0	1.16.0     	Rollback to 1 
```

11.查看端口是否更改回原来的30080

![](/img/2021-03-30/5.png)

应用回滚成功







声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。

