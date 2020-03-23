---
layout: post
title: 使用python生成sitemap并自动推送到百度站长
date: 2020-03-23
author: ZMY
header-img: img/post-bg-desk.jpg
catalog : true
tags:
    - python 
    - sitemap 
    - 百度站长自动推送
---

## <img class="original" src='https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/original.png'>使用python生成sitemap并自动推送到百度站长

## 背景
最近将网站收录到了百度站长平台里,为了让百度能够尽快收录我的网站，我使用的是主动推送中的curl提交和sitemap方式来加快blog的收录进程。  
并且之后再更新blog后，通过python脚本结合git工具，一次性提交sitemap并主动推送，达到快速更新blog地址及收录的作用  
## 前提条件
+ python3环境
+ 百度站长平台账号
+ blog能够通过域名访问
## 1.通过python生成sitemap.xml文件
