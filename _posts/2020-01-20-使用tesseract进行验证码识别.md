---
layout: post
title: 使用tesseract进行验证码识别
date: 2020-01-20
author: ZMY
header-img: 2020-01-20.png
tags:
    - tesseract
---
## <img class="original" src='https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/original.png'>使用tesseract进行验证码识别  
## 项目目的  
在使用python进行web爬虫过程中，验证码是一个无法绕过的问题，一些大型网站会采用比较高级的验证方式，如图片点选，滑动图片等等。  
今天进行的是较低一级的验证码图片的识别，即图片上的字母和数值上有横线如何进行识别。如下图，当然现今有很多站点提供api可供大家进行识别，我们要做的是如何在本地搭建一套这样的验证码识别系统，供自己使用  
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-01-20/captcha_show.png)  
对于像12306网站这种网站上的图片点验证码识别比较麻烦，应该使用的是神经网络识别系统，之后有时间会实践一下，更新一个专门关于神经网络识别验证码的博客。

## 软件环境
- 系统版本centos7.4.1708  
- python版本3.6.5  
- tesseract版本4.1.0  
- leptonica版本1.78.0(tesseract包的安装依赖)  
- PIL库图片过滤
- tesseract数据训练验证码  

## 安装及部署
### 一. 安装并编译leptonica
1. 安装依赖包  
```
#yum install gcc autoconf automake libtool libjpeg-devel libpng-devel libtiff-devel zlib-devel -y
```  
2. 下载leptonica-1.78.0并编译、加载环境变量      
```
#wget http://www.leptonica.org/source/leptonica-1.78.0.tar.gz
#tar xzvf leptonica-1.78.0.tar.gz
#cd leptonica-1.78.0
```
3. 编译并安装  
```
#./autogen.sh 
#./configure
#make
#make install
```
4. 添加环境变量  
```
#vim /etc/profile
```
5. 最后添加如下内容  
```
#export LD_LIBRARY_PATH=$LD_LIBRARY_PAYT:/usr/local/lib
#export LIBLEPT_HEADERSDIR=/usr/local/include
#export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig 
```
6. 执行如下命令使之立即生效  
```
#source /etc/profile
```
### 二.下载并安装tesseract4.1.0
1. 安装tesseract
```
#wget https://github.com/tesseract-ocr/tesseract/archive/4.1.0.tar.gz
#tar xzvf tesseract-4.1.0.tar.gz
#cd tesseract-4.1.0
```
2. 编译并安装
```
#./autogen.sh 
#./configure
#make
#make install
````
3. 查看tesseract版本
```
#tesseract --version
4.1.0
```
### 三.training的编译安装
1. 安装依赖库  
```
#yum install libicu-devel pango-devel cairo-devel -y
```
2. 下载并安装libarchive  
```
#wget http://www.libarchive.org/downloads/libarchive-3.3.3.tar.gz
#tar xzvf libarchive-3.3.3.tar.gz
#cd libarchive-3.3.3
###编译并安装
#./configure
#make
#make install
```
3. 下载安装icu52版本,不安装这个软件包training会包icu版本较低错误    
```
#wget http://download.icu-project.org/files/icu4c/52.1/icu4c-52_1-src.tgz
#tar -xvzf icu4c-52_1-src.tgz
#cd icu/source/
###编译并安装
#./runConfigureICU Linux --with-library-bits=64
#make -j 5
#make install
```
#创建软连接
```
#ln -s /usr/local/lib/libicui18n.so.52 /usr/lib64/libicui18n.so.52
#ln -s /usr/local/lib/libicuio.so.52 /usr/lib64/libicuio.so.52
#ln -s /usr/local/lib/libicuuc.so.52 /usr/lib64/libicuuc.so.52
#ln -s /usr/local/lib/libicudata.so.52 /usr/lib64/libicudata.so.5
```
5. 编译并安装traning
```
#./configure
#make training
#make training-install
```
6. 有如下提示training安装成功  
```
lstmtraining --version
4.1.0
```
### 四. 下载用于图片训练的验证码   
1. 去网上下载用于验证码训练的图片1000+张  
我使用的验证码sample：https://www.kaggle.com/fournierp/captcha-version-2-images 有兴趣可以自己制作验证码：https://pypi.org/project/captcha/ 
2. 将1000+张验证码图片分成二部分，一部分用于tesseract数据训练，一部分用于测试训练后的识别准确率  
```
待训练原始验证码存储路径:/root/samples_training/
待验证原始验证码存储路径:/root/samples_test/
```
### 五. 使用PIL库进行图片过滤
1. 
2. 
3. 
### 五. 对数据进行训练
1. 
2. 
3. 
### 六. 验证码识别验证
1. 
2. 
3. 

```
python代码
```
## 总结
