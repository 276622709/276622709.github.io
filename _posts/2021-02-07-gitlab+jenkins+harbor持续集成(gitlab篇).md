---
layout: post
title: gitlab+jenkins+harbor持续集成(gitlab篇)
date: 2021-02-07
author: ZMY
header-img: ../img/2021-02-07/background.png
catalog : true
tags:
   - kubernetes
   - gitlab
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>gitlab+jenkins+harbor持续集成(gitlab篇)

| 主机名/功能 | ip地址/访问方式              | 操作系统                      | 版本    | 备注   |
| ----------- | ---------------------------- | ----------------------------- | ------- | ------ |
| master      | 192.168.140.210              | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node1       | 192.168.140.211              | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node2       | 192.168.140.212              | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node3       | 192.168.140.213              | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| gitlab      | http://192.168.140.212:10000 |                               | v13.8.2 | 容器   |

[官方gitlab项目地址](https://github.com/sameersbn/docker-gitlab)

git命令下载github上gitlab项目安装包

```
# yum install git -y
# git clone https://github.com/sameersbn/docker-gitlab.git
# cd docker-gitlab/kubernetes
```

vim gitlab-svc.yml

```
apiVersion: v1
kind: Service
metadata:
  name: gitlab
  labels:
    name: gitlab
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: http
      nodePort: 10000
    - name: ssh
      port: 22
      targetPort: ssh
      nodePort: 10020
  selector:
    name: gitlab
```

vim gitlab-rc.yml 修改时间区域和登陆密码(至少8位)

```
- name: TZ
  value: Asia/Beijing
- name: GITLAB_TIMEZONE
  value: Beijing
- name: GITLAB_ROOT_PASSWORD
  value: ********

```

执行sh脚本

```
# sh deploy.sh
```

查看各pod状态,可以看到gitlab有问题

```
[root@master kubernetes]# kubectl get pod
NAME               READY   STATUS    RESTARTS   AGE
gitlab-7q4mq       0/1     Running   3          4m18s
postgresql-77f9h   1/1     Running   0          4m17s
redis-lpnbg        1/1     Running   0          4m16s
```

查看日志

```
# kubectl logs pod/gitlab-7q4mq -f
```

报错：

>psql:/home/git/gitlab/db/structure.sql:9: ERROR:  permission denied to create extension "btree_gist"
>HINT:  Must be superuser to create this extension.
>rake aborted!
>failed to execute:
>psql -v ON_ERROR_STOP=1 -q -X -f /home/git/gitlab/db/structure.sql --single-transaction gitlab_production
>
>Please check the output above for any errors and make sure that `psql` is installed in your PATH and has proper permissions.

解决办法：
参考[https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/5612](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/5612)

修改postgresql-rc.yml中DB_EXTENSION对应的值

```
- name: DB_EXTENSION
  value: pg_trgm,btree_gist
```

执行# sh teardown.sh清除错误环境

```
# sh teardown.sh
```

重新创建gitlab实验环境

```
# sh deploy.sh
```

**gitlab建立后访问时会出现的情况**

1.gitlab容器自动重启    
原因:内存不足，oom杀死gitlab容器，kubelet根据策略重启容器，然后gitlab消耗内存,oom杀死gitlab容器，循环下去 

2.gitlab所在容器节点变成不可用，且各节点轮流进去notReady状态    
原因:内存不足，负载过高，还没触发oom，节点不能及时响应状态检测，导致gitlab所在节点状态不可用，然后根据启动策略，控制节点通过计算在健康状态节点上启动gitlab，杀死原来不好用的节点的gitlab容器（然后gitlab又因为内存不足，导致，io负载过高，然后循环下去

解决办法：  
1.扩大物理机内存资源（因为我的是虚拟机环境，我直接扩展了内存资源）

2.限制gitlab使用资源，并预留systemd和kubernetes服务资源

**访问gitlab https://nodeip:10000**  
输入账号和密码进行登录  
![](/img/2021-02-07/1.png)
首页展示
![](/img/2021-02-07/2.png)

新建项目

![](/img/2021-02-07/3.png)

![](/img/2021-02-07/4.png)

![](/img/2021-02-07/5.png)





我这次实验的项目准备使用我之前用django弄的通过web方式输入命令，显示系统返回结果的项目。

clone原仓库库文件并push到新仓库中

```
# git clone https://github.com/276622709/django_first_display_the_result_of_system_command_in_the_html.git
# cd django_first_display_the_result_of_system_command_in_the_html
# git remove origin
git add origin
# git clone http://192.168.140.212:10000/root/django_docker.git
# git config user.name root
# git config user.email 2@2.com
# git add .
# git commit -m "."
# git push -u origin master
```

输入root用户名和密码

```
Username for 'http://192.168.140.212:10000': root
Password for 'http://root@192.168.140.212:10000': 
Counting objects: 119, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (91/91), done.
Writing objects: 100% (119/119), 224.24 KiB | 0 bytes/s, done.
Total 119 (delta 20), reused 119 (delta 20)
remote: Resolving deltas: 100% (20/20), done.
To http://192.168.140.212:10000/root/django_docker.git
 * [new branch]      master -> master
分支 master 设置为跟踪来自 origin 的远程分支 master。
```

返回项目中，可以看到项目文件已上传成功

![](/img/2021-02-07/6.png)





搭建gitlab是为了配合jenkins完成代码自动化部署过程，在后面搭建jenkins博客中还会有涉及到gitlab操作的步骤，到时候一起介绍  
blog已更新[gitlab+jenkins+harbor持续集成(jenkins篇)](https://276622709.github.io/2021/02/15/k8s%E9%83%A8%E7%BD%B2jenkins%E4%B8%8Egitlab%E5%AE%9E%E7%8E%B0%E8%87%AA%E5%8A%A8%E5%8C%96%E9%83%A8%E7%BD%B2/)



声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。
