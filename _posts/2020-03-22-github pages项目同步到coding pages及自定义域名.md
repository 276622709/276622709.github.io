---
layout: post
title: github pages项目同步到coding pages及自定义域名
date: 2020-03-022
author: ZMY
header-img: img/post-bg-desk.jpg
catalog : true
tags:
    - coding pages
---
## <img class="original" src='https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/original.png'>github pages项目同步到coding pages及自定义域名
## 背景
使用GitHub pages做blog的同学可能都知道，要想别人通过搜索引擎找到自己的内容，最好的方式就是通过搜索引擎收录自己的网址。但是通过实践发现，google可以收录自己的网站，但是百度不行（历史原因，自行了解下）  
因此如何将自己的blog收录到百度内，是很多在github pages做blog要解决的问题。解决的办法有很多，我这里介绍的是如何通过coding pages解决这个问题。 
## 准备条件
+ 已在github pages上有自己的网站  
+ coding已注册账号(没账号需要申请官网[](https://coding.net))  
+ 新网已注册账号（或其他域名申请平台）  
## 1.coding操作过程
### 1.1新建项目
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/1.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/2.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/3.png)
### 1.2 同步github库到本地
命令参考我之前的blog <https://276622709.github.io/2018/09/28/github%E5%88%9D%E6%AD%A5%E4%BD%BF%E7%94%A8/>
### 1.3 将上一步同步到本地的github库内容同步到coding库中
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/4.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/5.png)
这里需要将第一个命令修改一下，因为之前已经添加了一个origin，这里不修改的话会报错，修改后内容见下图
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/6.png)
### 1.4 返回到coding，构建网站
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/7.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/8.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/9.png)
### 1.5 部署网站
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/10.png)
出现绿色图标即为部署成功，有错误请参考日志内容改正  
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/11.png)
### 1.6 验证是否同步成功
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/12.png)

## 2.自定义域名
域名注册（注册账号，添加信息我这里省略了，我是在新网上注册的，这里你可以自由选择）  
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/13.png)
绑定信息后，返回到coding，添加自定义域名信息  
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/14.png)
验证自定义网址是否成功，这里会有一定的延迟
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-22/15.png)
接下来通过百度站长工具就可以收录我们的网址了（这里就不赘述了，网上有很多这样的攻略）  

对了，之前在网上搜索解决方案的时候，搜索到了一个zeit的解决办法<https://zeit.co/>自己实践过，方法可行，而且很方便，github上更新的信息会自动同步到zeit上，而coding需要到客户端手动执行同步，但是有一点，使用zeit方案的话访问http时候会自动挑战到https，状态码是307，而百度收录的时候只会收录状态码是301的redirect，因此我最后选择了coding方案  






