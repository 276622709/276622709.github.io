---
layout: post
title: 自由门软件添加国内网站
header-img: img/post-bg-coffee.jpeg
date: 2018-9-30
auth: ZMY
tags:
    - freegate

---
## 自由门软件国内网站直通添加网址  
### 背景  
最近使用的亚马逊云免费12月的云主机到期了....申请新号新注册又给封了(记得以前没那么严，10几块钱就能在某宝买一个虚拟visa信用卡，现在某宝没卖的了，60块钱某宝直接买的账号，用了不到2天就被封了...)，然后转到免费的freegate软件上了，可是每次使用很麻烦，不能像ss那样，访问国内的就自动跳过ss；freegate得手动添加网址(默认只有常用的10多个网址，什么百度，qq，淘宝等)，才能跳过代理，这里问题来了，上哪里去找大批量的国内网址并添加呢？
### 目的
解决自由门软件国内网站直通只有自带的10多个常用网站的问题  
### 解决办法  
通过github上别人获取的国内白名单列表，导入自由门网站直通选项里  


1.首先得下载个自由门软件即freegate软件[下载链接](http://dongtaiwang.com/loc/download.en.php)  
2.查看一下需要添加的地址格式  
![](img/freegate/free_gate_address_format.png)  
3.找个国内网站地址集 
这里发现github上有gfw_whitelist项目比较符合我们的要求  
[gfw_whitelist](https://github.com/breakwa11/gfw_whitelist)  
4.源文件下载地址  
[whitelist](https://github.com/breakwa11/gfw_whitelist/raw/master/whitelist.pac)  
5.将源文件里需要的数据保留，其他没用的都删除(有用的数据只有white_domains变量里的数据)  
可以看到原文件中有用的数据格式是已字典的形式存在的，下一步我准备用python将源文件里面需要的数据进行格式转换 
![](https://github.com/276622709/276622709.github.io/blob/master/img/freegate/original_file_date.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/freegate/original_file_date.png)
<img src="https://github.com/276622709/276622709.github.io/blob/master/img/freegate/original_file_date.png"></img>
6.编写python代码保存为whitelist.pac.1文件
```python
white_domains = {"am":{
"126":1,
"51":1
},"biz":{
"7daysinn":1,
"baozhuang":1,
"bengfa":1,
"changan":1,
.....略}
for key,value in white_domains.items():
  print '.'+key
  for a,b in value.items():
    print '.'+a+'.'+key
```
代码源文件下载地址[下载代码源文件](https://github.com/276622709/276622709.github.io/blob/master/code/freegate/whitelist.pac.1)  
7.执行python  
```python
python whitelist.pac.1 > whitelist
```
这样就将需要的域名格式填入whitelist文件中  
whitelist内容如下  
![](https://github.com/276622709/276622709.github.io/blob/master/img/freegate/white_list_content.png)
8.将whitelist里面的内容粘贴到自由门软件，国内软件直通选项里，最后保存即可(建议添加之前，先保留一份原数据配置文件，方便以后回档操作)
备份原数据配置文件位置如下
![](https://github.com/276622709/276622709.github.io/blob/master/img/freegate/freegate_data_file.png)
这里有个问题粘贴的时候如何直接粘贴会都粘贴到一行，原因是通过linux传到windows的文件，最后的换行符不一样(linux为\n,windows为\r\n)  
因此这里我用notepad+软件-》编辑-》文档格式转化-》转换为windows格式解决(即先将whitelist文件传到windows上，再通过notepad+软件转换格式，再复制whitelist里面的内容)    
9.由于我的电脑是winxp 32位的，所以测试了一下最多能添300个地址，然后软件就卡那了......，要么是我系统的原因，要么是软件的原因....
这里只提供个思路供大家参考  




