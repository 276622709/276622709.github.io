---
layout: post
title: 初步使用github的pull和push功能
date: 2018-9-28
author: ZMY
header-img: img/post-bg-universe.jpg
tags:
    - github
---
## github初步使用教程
### 目的
通过github的pull和push功能，将之前fork的项目里的文件批量删除，并同步  
### 准备工作
1.我的操作系统是centos7，github账号申请可访问[github账号申请](https://github.com/)   
2.已经使用fork功能clone了一个别人的项目 
### 操作过程 
1.使用yum安装git命令  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_install.png)  
2.创建一个目录zhai_git(用于git项目使用)  
使用cd命令进入到zhai_git中  
初始化git  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_init.png)  
3.把文件添加到暂存区里去(add后面有个点,意为当前文件夹下的所有文件)  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_add_cache.png)  
4.使用git commit命令告诉git把文件提交到仓库(这里为copy远程文件到问题，因此返回内容提示nothing to commit)  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_commit.png)  
5.找到需要pull的项目地址  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/find_pull_project_address.png)  
6.添加需要pull的项目地址  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/add_remote_address.png)  
7.pull远程数据到本地  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/pull_data.png)  
8.完成上面命令后项目文件就下载到当前目录下了  
修改文件后，同步本地仓库到远端使用git push命令  
实际上是把当前分支master推送到远程。执行此命令后会要求输入用户名、密码，验证通过后即开始上传。  
在上传之前需要使用git add命令将目录下修改的内容添加进暂存区中(-A可以同步删除的文件，不加-A只包括修改和新增的文件)  
然后使用git commit 提交这次的commit注释  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_commit_again.png)  
9.git commit后提示下面信息  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_commit_post_info.png)  
10.然后使用git push上传  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_push_order.png)  
11.填写账号和密码信息，成功连接后，同步信息如下  
![](https://github.com/276622709/276622709.github.io/blob/master/img/github/git_push_return_info.png)  
