---
layout: post
title: 使用python生成sitemap并自动推送到百度站长
date: 2020-03-23
author: ZMY
header-img: ../img/post-bg-desk.jpg
catalog : true
tags:
    - python 
    - sitemap 
    - 百度站长自动推送
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>使用python生成sitemap并自动推送到百度站长

## 背景
最近将网站收录到了百度站长平台里,为了让百度能够尽快收录我的网站，我使用的是主动推送中的curl提交和sitemap方式来加快blog的收录进程。  
并且之后再更新blog后，通过python脚本结合git工具，一次性提交sitemap并主动推送，达到快速更新blog地址及收录的作用  
## 前提条件
+ python3环境
+ 百度站长平台账号
+ blog能够通过域名访问

## 1.通过python生成sitemap.xml文件
安装reppy模块,并下载py脚本
```
#pip3 install reppy
#wget https://raw.githubusercontent.com/276622709/276622709.github.io/master/code/2020-03-23/sitemap_gen_baidu_auto_push.py
```
其中sitemap_gen_baidu_auto_push.py是自己修改的，你需要修改脚本中的变量curloption,变量值为百度站长中你自己拥有的curl命令脚本  
![](/img/2020-03-23/1.png)

项目参考地址<http://toncar.cz/opensource/sitemap_gen.html>  
## 2.执行脚本命令生成sitemap.xml,并将博客网址主动推送给百度站长平台
```
#python sitemap_gen_baidu_auto_push.py -o sitemap.xml -c always http://www.zmy024.cn
```
如下图所示出现success即为成功   
![](/img/2020-03-23/2.png)
## 3.git更新blog和sitemap.xml文件
参考之前我写的blog
<https://276622709.github.io/2018/09/28/github%E5%88%9D%E6%AD%A5%E4%BD%BF%E7%94%A8/>
## 4.登陆百度站长平台将自己博客的sitemap.xml网址添加
![](/img/2020-03-23/3.png)
![](/img/2020-03-23/4.png)
以后每次更新博客后通过该脚本即可主动更新sitemap.xml内容并推送给百度站长平台    

声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。
