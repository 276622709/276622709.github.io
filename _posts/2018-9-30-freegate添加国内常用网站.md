---

---
## 自由门软件国内网站直通添加网址  
### 目的  
解决自由门软件国内网站直通只有自带的10多个常用网站的问题  
### 解决办法  
通过github上别人获取的国内白名单列表，导入自由门网站直通选项里  


1.首先得下载个自由门软件(自行百度)  
2.查看一下需要添加的地址格式  
![]()  
3.下载个需要导入的文件  
原项目地址  
![](https://github.com/breakwa11/gfw_whitelist)  
4.原文件下载地址  
![](https://github.com/breakwa11/gfw_whitelist/raw/master/whitelist.pac)  
5.将源文件里需要的数据保留，其他没用的都删除  
可以看到原文件中有用的数据格式是已字典的形式存在的，这里我用python将原文件里面需要的数据进行格式转换  
6.编写python代码  
white_domains = {"am":{  
"126":1,  
"51":1  
},"biz":{  
"7daysinn":1,  
"baozhuang":1,  
"bengfa":1,  
"changan":1,  
.....}  
for key,value in white_domains.items():  
  print '.'+key  
  for a,b in value.items():  
    print '.'+a+'.'+key  
代码源文件下载地址[]()  

7.执行python  
python whitelist.pac.1 > whitelist  
8.将whitelist里面的内容粘贴到自由门软件，国内软件直通选项里(建议添加之前，先保留一份原配置文件，方便以后回档操作)



